import tkinter as tk
from tkinter import ttk
import json
from datetime import datetime
import threading
import time
from elasticsearch import Elasticsearch
import requests
from PIL import Image, ImageTk
import io

class PhysicalDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("SIEM Physical Dashboard")
        self.root.attributes('-fullscreen', True)
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure("Alert.TLabel", foreground="red", font=('Helvetica', 12, 'bold'))
        self.style.configure("Normal.TLabel", font=('Helvetica', 10))
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create widgets
        self.create_widgets()
        
        # Initialize Elasticsearch client
        self.es = Elasticsearch(['http://localhost:9200'])
        
        # Start update thread
        self.update_thread = threading.Thread(target=self.update_data, daemon=True)
        self.update_thread.start()
        
        # Bind escape key to exit
        self.root.bind('<Escape>', lambda e: self.root.quit())

    def create_widgets(self):
        # Status indicators
        self.status_frame = ttk.LabelFrame(self.main_frame, text="System Status", padding="5")
        self.status_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.elasticsearch_status = ttk.Label(self.status_frame, text="Elasticsearch: Checking...")
        self.elasticsearch_status.grid(row=0, column=0, padx=5)
        
        self.morpheus_status = ttk.Label(self.status_frame, text="Morpheus: Checking...")
        self.morpheus_status.grid(row=0, column=1, padx=5)
        
        # Alert counter
        self.alert_frame = ttk.LabelFrame(self.main_frame, text="Alert Summary", padding="5")
        self.alert_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.critical_alerts = ttk.Label(self.alert_frame, text="Critical: 0", style="Alert.TLabel")
        self.critical_alerts.grid(row=0, column=0, padx=5)
        
        self.high_alerts = ttk.Label(self.alert_frame, text="High: 0", style="Alert.TLabel")
        self.high_alerts.grid(row=0, column=1, padx=5)
        
        # Recent alerts
        self.alerts_frame = ttk.LabelFrame(self.main_frame, text="Recent Alerts", padding="5")
        self.alerts_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.alerts_text = tk.Text(self.alerts_frame, height=10, width=50)
        self.alerts_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # System metrics
        self.metrics_frame = ttk.LabelFrame(self.main_frame, text="System Metrics", padding="5")
        self.metrics_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.total_events = ttk.Label(self.metrics_frame, text="Total Events: 0")
        self.total_events.grid(row=0, column=0, padx=5)
        
        self.processed_events = ttk.Label(self.metrics_frame, text="Processed Events: 0")
        self.processed_events.grid(row=0, column=1, padx=5)

    def update_data(self):
        while True:
            try:
                # Check Elasticsearch status
                es_health = self.es.cluster.health()
                self.elasticsearch_status.config(
                    text=f"Elasticsearch: {es_health['status'].upper()}",
                    foreground="green" if es_health['status'] == 'green' else "orange"
                )
                
                # Get alert counts
                query = {
                    "size": 0,
                    "aggs": {
                        "severity_counts": {
                            "terms": {
                                "field": "severity.keyword"
                            }
                        }
                    }
                }
                
                response = self.es.search(index="logstash-*_analyzed", body=query)
                buckets = response['aggregations']['severity_counts']['buckets']
                
                severity_counts = {bucket['key']: bucket['doc_count'] for bucket in buckets}
                
                self.critical_alerts.config(text=f"Critical: {severity_counts.get('critical', 0)}")
                self.high_alerts.config(text=f"High: {severity_counts.get('high', 0)}")
                
                # Get recent alerts
                recent_alerts = self.es.search(
                    index="logstash-*_analyzed",
                    body={
                        "size": 5,
                        "sort": [{"@timestamp": "desc"}],
                        "query": {
                            "bool": {
                                "must": [
                                    {"exists": {"field": "severity"}}
                                ]
                            }
                        }
                    }
                )
                
                self.alerts_text.delete(1.0, tk.END)
                for hit in recent_alerts['hits']['hits']:
                    source = hit['_source']
                    alert_text = f"{source['@timestamp']} - {source['severity']}: {source['message']}\n"
                    self.alerts_text.insert(tk.END, alert_text)
                
                # Update metrics
                total_events = self.es.count(index="logstash-*")['count']
                processed_events = self.es.count(index="logstash-*_analyzed")['count']
                
                self.total_events.config(text=f"Total Events: {total_events}")
                self.processed_events.config(text=f"Processed Events: {processed_events}")
                
            except Exception as e:
                print(f"Error updating dashboard: {str(e)}")
            
            time.sleep(5)  # Update every 5 seconds

def main():
    root = tk.Tk()
    app = PhysicalDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
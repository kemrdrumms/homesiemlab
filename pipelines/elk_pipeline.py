from elasticsearch import Elasticsearch
from datetime import datetime
import json
import time

class LogProcessor:
    def __init__(self, es_host, es_index):
        self.es = Elasticsearch([es_host])
        self.index = es_index
        self.last_timestamp = None

    def process_logs(self):
        query = {
            "size": 1000,
            "sort": [{"@timestamp": "asc"}],
            "query": {
                "bool": {
                    "must": [
                        {"exists": {"field": "message"}}
                    ]
                }
            }
        }
        
        if self.last_timestamp:
            query["query"]["bool"]["filter"] = [
                {"range": {"@timestamp": {"gt": self.last_timestamp}}}
            ]

        response = self.es.search(
            index=self.index,
            size=query["size"],
            sort=query["sort"],
            query=query["query"]
        )
        hits = response['hits']['hits']
        
        if hits:
            self.last_timestamp = hits[-1]['_source']['@timestamp']
            
            # Process and analyze logs
            for hit in hits:
                source = hit['_source']
                # Add analysis results
                source['analyzed'] = True
                source['severity'] = self.determine_severity(source['message'])
                
                # Store results
                self.es.index(
                    index=f"{self.index}_analyzed",
                    document=source
                )

    def determine_severity(self, message):
        # Simple severity determination based on keywords
        if any(word in message.lower() for word in ['critical', 'error', 'failed']):
            return 'critical'
        elif any(word in message.lower() for word in ['warning', 'unauthorized']):
            return 'high'
        elif any(word in message.lower() for word in ['notice', 'info']):
            return 'medium'
        return 'low'

def main():
    # Configuration
    es_host = "http://localhost:9200"
    es_index = "logstash-*"
    
    # Create processor
    processor = LogProcessor(es_host, es_index)
    
    # Process logs
    while True:
        try:
            processor.process_logs()
        except Exception as e:
            print(f"Error processing logs: {str(e)}")
        
        # Wait before next processing
        time.sleep(5)

if __name__ == "__main__":
    main() 
from flask import Flask, render_template, jsonify
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import json

app = Flask(__name__)
es = Elasticsearch(['http://localhost:9200'])

def get_recent_logs(limit=10):
    """Get recent logs from Elasticsearch"""
    query = {
        "size": limit,
        "sort": [{"@timestamp": "desc"}],
        "query": {
            "bool": {
                "must": [
                    {"exists": {"field": "message"}}
                ]
            }
        }
    }
    
    response = es.search(
        index="logstash-*",
        size=limit,
        sort=query["sort"],
        query=query["query"]
    )
    
    return [hit['_source'] for hit in response['hits']['hits']]

def get_alert_summary():
    """Get summary of alerts by severity"""
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
    
    response = es.search(
        index="logstash-*_analyzed",
        size=0,
        aggs=query["aggs"]
    )
    
    return response['aggregations']['severity_counts']['buckets']

@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')

@app.route('/api/logs')
def get_logs():
    """API endpoint for recent logs"""
    logs = get_recent_logs()
    return jsonify(logs)

@app.route('/api/alerts')
def get_alerts():
    """API endpoint for alert summary"""
    alerts = get_alert_summary()
    return jsonify(alerts)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 
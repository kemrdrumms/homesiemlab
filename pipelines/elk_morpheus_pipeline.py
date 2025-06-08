from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import json
from morpheus.config import Config
from morpheus.pipeline import LinearPipeline
from morpheus.stages.input.elasticsearch_source_stage import ElasticsearchSourceStage
from morpheus.stages.preprocess.deserialize_stage import DeserializeStage
from morpheus.stages.preprocess.preprocess_log_stage import PreprocessLogStage
from morpheus.stages.inference.triton_inference_stage import TritonInferenceStage
from morpheus.stages.postprocess.serialize_stage import SerializeStage
from morpheus.stages.output.elasticsearch_sink_stage import ElasticsearchSinkStage

class ElasticsearchSourceStage:
    def __init__(self, config, es_host, es_index, query_size=1000):
        self.es = Elasticsearch([es_host])
        self.index = es_index
        self.query_size = query_size
        self.last_timestamp = None

    def get_data(self):
        query = {
            "size": self.query_size,
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

        response = self.es.search(index=self.index, body=query)
        hits = response['hits']['hits']
        
        if hits:
            self.last_timestamp = hits[-1]['_source']['@timestamp']
        
        return [hit['_source'] for hit in hits]

def build_pipeline(config: Config, es_host: str, es_index: str):
    # Create pipeline
    pipeline = LinearPipeline(config)
    
    # Add stages
    pipeline.set_source(ElasticsearchSourceStage(config, es_host, es_index))
    pipeline.add_stage(DeserializeStage(config))
    pipeline.add_stage(PreprocessLogStage(config))
    pipeline.add_stage(TritonInferenceStage(config, model_name="log_anomaly_detection"))
    pipeline.add_stage(SerializeStage(config))
    pipeline.add_stage(ElasticsearchSinkStage(config, es_host, f"{es_index}_analyzed"))
    
    return pipeline

if __name__ == "__main__":
    # Create config
    config = Config()
    config.model_max_batch_size = 8
    config.pipeline_batch_size = 1024
    config.feature_length = 256
    
    # Elasticsearch configuration
    es_host = "http://localhost:9200"
    es_index = "logstash-*"
    
    # Build and run pipeline
    pipeline = build_pipeline(config, es_host, es_index)
    pipeline.run() 
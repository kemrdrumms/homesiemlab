import os
from morpheus.config import Config
from morpheus.pipeline import LinearPipeline
from morpheus.stages.input.file_source_stage import FileSourceStage
from morpheus.stages.preprocess.deserialize_stage import DeserializeStage
from morpheus.stages.preprocess.preprocess_log_stage import PreprocessLogStage
from morpheus.stages.inference.triton_inference_stage import TritonInferenceStage
from morpheus.stages.postprocess.serialize_stage import SerializeStage
from morpheus.stages.output.write_to_file_stage import WriteToFileStage

def build_pipeline(config: Config):
    # Create pipeline
    pipeline = LinearPipeline(config)
    
    # Add stages
    pipeline.set_source(FileSourceStage(config, filename=config.input_file))
    pipeline.add_stage(DeserializeStage(config))
    pipeline.add_stage(PreprocessLogStage(config))
    pipeline.add_stage(TritonInferenceStage(config, model_name="log_anomaly_detection"))
    pipeline.add_stage(SerializeStage(config))
    pipeline.add_stage(WriteToFileStage(config, filename=config.output_file))
    
    return pipeline

if __name__ == "__main__":
    # Create config
    config = Config()
    config.input_file = "logs/sample.log"
    config.output_file = "logs/detections.json"
    config.model_max_batch_size = 8
    config.pipeline_batch_size = 1024
    config.feature_length = 256
    
    # Build and run pipeline
    pipeline = build_pipeline(config)
    pipeline.run() 
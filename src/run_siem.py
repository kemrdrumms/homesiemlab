import os
import json
import logging
from datetime import datetime
from pathlib import Path
from morpheus.config import Config
from pipelines.log_analysis_pipeline import build_pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/siem.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_config():
    """Load detection rules and configuration"""
    config_path = Path('config/detection_rules.json')
    with open(config_path) as f:
        return json.load(f)

def setup_directories():
    """Ensure all required directories exist"""
    directories = ['logs', 'models', 'config', 'pipelines']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def main():
    try:
        # Setup
        setup_directories()
        config = load_config()
        logger.info("Starting SIEM system...")
        
        # Initialize Morpheus config
        morpheus_config = Config()
        morpheus_config.input_file = "logs/sample.log"
        morpheus_config.output_file = f"logs/detections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        morpheus_config.model_max_batch_size = 8
        morpheus_config.pipeline_batch_size = 1024
        morpheus_config.feature_length = 256
        
        # Build and run pipeline
        pipeline = build_pipeline(morpheus_config)
        logger.info("Pipeline built successfully")
        
        # Run the pipeline
        pipeline.run()
        logger.info("Pipeline execution completed")
        
    except Exception as e:
        logger.error(f"Error running SIEM: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 
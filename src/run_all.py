import subprocess
import sys
import time
import os
from threading import Thread

def run_log_generator():
    """Run the log generator in a separate process"""
    subprocess.run([sys.executable, "src/log_generator.py"])

def run_web_app():
    """Run the Flask web application"""
    subprocess.run([sys.executable, "src/web_app.py"])

def run_log_processor():
    """Run the log processor"""
    subprocess.run([sys.executable, "pipelines/elk_pipeline.py"])

def main():
    print("Starting SIEM System...")
    
    # Start log generator in a separate thread
    generator_thread = Thread(target=run_log_generator)
    generator_thread.daemon = True
    generator_thread.start()
    
    # Start log processor in a separate thread
    processor_thread = Thread(target=run_log_processor)
    processor_thread.daemon = True
    processor_thread.start()
    
    # Run web app in main thread
    run_web_app()

if __name__ == "__main__":
    main() 
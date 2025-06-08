# Homemade SIEM Lab

A lightweight Security Information and Event Management (SIEM) system built with Python, Elasticsearch, and Flask. This project demonstrates the implementation of a basic SIEM system that can collect, analyze, and visualize security logs.

## Features

- Real-time log collection and analysis
- Web-based dashboard for log visualization
- Alert generation based on log severity
- Elasticsearch integration for log storage
- Customizable log patterns and detection rules
- Production-ready deployment guide

## Architecture

The system consists of three main components:
1. Log Generator/Collector
2. Log Processor/Analyzer
3. Web Dashboard

## Prerequisites

- Python 3.8+
- Elasticsearch 7.x
- Modern web browser

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/homemade-siem-lab.git
cd homemade-siem-lab
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start Elasticsearch (make sure it's installed and running)

4. Run the system:
```bash
python src/run_all.py
```

5. Access the dashboard at `http://localhost:5000`

## Project Structure

```
homemade-siem-lab/
├── src/
│   ├── web_app.py          # Flask web application
│   ├── log_generator.py    # Log generation/collection
│   └── run_all.py         # Main runner script
├── pipelines/
│   └── elk_pipeline.py    # Log processing pipeline
├── templates/
│   └── index.html         # Dashboard template
├── requirements.txt       # Python dependencies
└── PRODUCTION_DEPLOYMENT.txt  # Deployment guide
```

## Development

This project is designed for learning and experimentation. Feel free to:
- Add new log patterns
- Implement custom detection rules
- Enhance the dashboard
- Add more analysis features

## Security Note

This is a learning project and should not be used in production without proper security hardening. See PRODUCTION_DEPLOYMENT.txt for production deployment guidelines.

## License

MIT License - feel free to use this project for learning and experimentation.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 
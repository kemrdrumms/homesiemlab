from elasticsearch import Elasticsearch
import random
import time
from datetime import datetime
import json

# Sample log patterns
LOG_PATTERNS = {
    'normal': [
        "User {user} logged in successfully",
        "File {file} accessed by {user}",
        "Database query completed in {time}ms",
        "Backup completed successfully",
        "System check completed - all systems operational"
    ],
    'warning': [
        "High CPU usage detected: {cpu}%",
        "Memory usage above threshold: {mem}%",
        "Multiple failed login attempts from IP {ip}",
        "Database connection pool near capacity",
        "Backup taking longer than usual"
    ],
    'error': [
        "Failed to connect to database: {error}",
        "Authentication failed for user {user}",
        "File access denied: {file}",
        "Service {service} failed to start",
        "Network timeout when connecting to {host}"
    ],
    'critical': [
        "CRITICAL: Database corruption detected",
        "CRITICAL: Multiple services down",
        "CRITICAL: Security breach attempt detected",
        "CRITICAL: System resources exhausted",
        "CRITICAL: Unauthorized access attempt from {ip}"
    ]
}

# Sample data for log generation
USERS = ['admin', 'john.doe', 'jane.smith', 'system', 'backup']
FILES = ['/var/log/system.log', '/etc/config.json', '/data/backup.tar', '/home/user/file.txt']
SERVICES = ['nginx', 'apache', 'mysql', 'redis', 'elasticsearch']
ERRORS = ['Connection refused', 'Timeout', 'Permission denied', 'Resource not found']
IPS = ['192.168.1.{}', '10.0.0.{}', '172.16.0.{}']

class LogGenerator:
    def __init__(self, es_host='http://localhost:9200'):
        self.es = Elasticsearch([es_host])
        self.index = 'logstash-{}'.format(datetime.now().strftime('%Y.%m.%d'))

    def generate_log(self):
        # Randomly select log type with weighted probability
        log_type = random.choices(
            ['normal', 'warning', 'error', 'critical'],
            weights=[70, 20, 8, 2]
        )[0]
        
        # Select random pattern
        pattern = random.choice(LOG_PATTERNS[log_type])
        
        # Fill in the pattern with random data
        log_data = {
            'message': pattern.format(
                user=random.choice(USERS),
                file=random.choice(FILES),
                time=random.randint(10, 1000),
                cpu=random.randint(80, 95),
                mem=random.randint(85, 98),
                ip=random.choice(IPS).format(random.randint(1, 254)),
                error=random.choice(ERRORS),
                service=random.choice(SERVICES),
                host=f"server{random.randint(1, 5)}.example.com"
            ),
            '@timestamp': datetime.now().isoformat(),
            'severity': log_type,
            'source': f"server{random.randint(1, 5)}",
            'environment': 'production'
        }
        
        return log_data

    def send_log(self, log_data):
        try:
            self.es.index(index=self.index, document=log_data)
            print(f"Sent log: {log_data['message']}")
        except Exception as e:
            print(f"Error sending log: {str(e)}")

    def run(self, interval=1, duration=60):
        """Generate logs for specified duration"""
        end_time = time.time() + duration
        while time.time() < end_time:
            log_data = self.generate_log()
            self.send_log(log_data)
            time.sleep(interval)

def main():
    generator = LogGenerator()
    print("Starting log generation...")
    print("Press Ctrl+C to stop")
    try:
        while True:
            generator.run(duration=1)  # Generate logs continuously
    except KeyboardInterrupt:
        print("\nStopping log generation...")

if __name__ == "__main__":
    main() 
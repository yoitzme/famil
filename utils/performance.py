import time
import streamlit as st
from functools import wraps
import psutil
import threading

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'response_times': [],
            'memory_usage': [],
            'cpu_usage': [],
            'active_connections': 0
        }
        self.start_monitoring()
    
    def monitor_resources(self):
        """Monitor system resources periodically."""
        while True:
            self.metrics['memory_usage'].append(psutil.Process().memory_info().rss / 1024 / 1024)
            self.metrics['cpu_usage'].append(psutil.Process().cpu_percent())
            time.sleep(60)  # Update every minute
    
    def start_monitoring(self):
        """Start resource monitoring in background."""
        thread = threading.Thread(target=self.monitor_resources, daemon=True)
        thread.start()
    
    def track_response_time(self, func):
        """Decorator to track function response times."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            self.metrics['response_times'].append(end_time - start_time)
            return result
        return wrapper
    
    def get_performance_report(self):
        """Generate performance report."""
        return {
            'avg_response_time': sum(self.metrics['response_times']) / len(self.metrics['response_times']) if self.metrics['response_times'] else 0,
            'max_response_time': max(self.metrics['response_times']) if self.metrics['response_times'] else 0,
            'avg_memory_usage': sum(self.metrics['memory_usage']) / len(self.metrics['memory_usage']) if self.metrics['memory_usage'] else 0,
            'peak_memory_usage': max(self.metrics['memory_usage']) if self.metrics['memory_usage'] else 0,
            'active_connections': self.metrics['active_connections']
        }

performance_monitor = PerformanceMonitor() 
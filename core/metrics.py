"""
metrics.py
==========

Performance tracking for scaling decisions.

Tracks operation duration and logs slow operations.
This data helps decide when to:
- Add caching (frequent repeated queries)
- Upgrade storage (slow disk I/O)
- Add servers (high CPU usage)

Usage:
    from core.metrics import track_performance
    
    class DataManager:
        @track_performance("data_download")
        def get_data(self, symbol, timeframe, start, end):
            ...

Output:
    INFO: data_download took 2.34s
    WARNING: SLOW: data_download took 15.23s (threshold: 10s)

Author: EdgeLab Development
Version: 1.0
"""

import time
import logging
from functools import wraps
from typing import Callable, Optional, Dict, Any
from datetime import datetime
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('edgelab.metrics')


# In-memory metrics storage (for MVP)
# In production, this would go to a metrics service
_metrics_store: Dict[str, list] = defaultdict(list)


def track_performance(
    operation: str,
    slow_threshold_seconds: float = 10.0,
    log_all: bool = True
):
    """
    Decorator to track operation performance.
    
    Args:
        operation: Name of operation (e.g., 'data_download', 'backtest_run')
        slow_threshold_seconds: Log warning if operation exceeds this
        log_all: If True, log all operations. If False, only log slow ones.
    
    Example:
        @track_performance("data_download", slow_threshold_seconds=5.0)
        def download_data(symbol):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                success = True
                error_msg = None
            except Exception as e:
                success = False
                error_msg = str(e)
                raise
            finally:
                duration = time.time() - start_time
                
                # Store metric
                _metrics_store[operation].append({
                    'timestamp': datetime.now().isoformat(),
                    'duration': duration,
                    'success': success,
                    'error': error_msg
                })
                
                # Keep only last 1000 entries per operation
                if len(_metrics_store[operation]) > 1000:
                    _metrics_store[operation] = _metrics_store[operation][-1000:]
                
                # Log performance
                if duration > slow_threshold_seconds:
                    logger.warning(
                        f"SLOW: {operation} took {duration:.2f}s "
                        f"(threshold: {slow_threshold_seconds}s)"
                    )
                elif log_all:
                    logger.info(f"{operation} took {duration:.2f}s")
            
            return result
        return wrapper
    return decorator


def get_metrics_summary(operation: Optional[str] = None) -> Dict[str, Any]:
    """
    Get summary statistics for tracked operations.
    
    Args:
        operation: Specific operation name, or None for all operations
    
    Returns:
        Dictionary with performance statistics
    """
    if operation:
        operations = {operation: _metrics_store.get(operation, [])}
    else:
        operations = dict(_metrics_store)
    
    summary = {}
    
    for op_name, metrics in operations.items():
        if not metrics:
            continue
        
        durations = [m['duration'] for m in metrics]
        successes = [m['success'] for m in metrics]
        
        summary[op_name] = {
            'count': len(metrics),
            'success_rate': sum(successes) / len(successes) * 100,
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'slow_count': sum(1 for d in durations if d > 10),
            'last_run': metrics[-1]['timestamp'] if metrics else None
        }
    
    return summary


def clear_metrics(operation: Optional[str] = None) -> None:
    """
    Clear stored metrics.
    
    Args:
        operation: Specific operation to clear, or None for all
    """
    if operation:
        _metrics_store[operation] = []
    else:
        _metrics_store.clear()


def log_scaling_recommendations() -> None:
    """
    Analyze metrics and log scaling recommendations.
    
    Call periodically (e.g., daily) to get optimization hints.
    """
    summary = get_metrics_summary()
    
    if not summary:
        logger.info("No metrics collected yet")
        return
    
    print("\n" + "=" * 50)
    print("SCALING RECOMMENDATIONS")
    print("=" * 50)
    
    for op_name, stats in summary.items():
        print(f"\n{op_name}:")
        print(f"  Total calls: {stats['count']}")
        print(f"  Success rate: {stats['success_rate']:.1f}%")
        print(f"  Avg duration: {stats['avg_duration']:.2f}s")
        print(f"  Slow operations: {stats['slow_count']}")
        
        # Recommendations
        if stats['avg_duration'] > 5:
            print(f"  RECOMMENDATION: Consider caching for {op_name}")
        
        if stats['slow_count'] > stats['count'] * 0.1:
            print(f"  RECOMMENDATION: >10% slow calls. Upgrade storage or add servers.")
        
        if stats['success_rate'] < 95:
            print(f"  RECOMMENDATION: High failure rate. Check error logs.")
    
    print("\n" + "=" * 50)


class MetricsContext:
    """
    Context manager for tracking complex operations.
    
    Usage:
        with MetricsContext("complex_backtest") as ctx:
            # Do work
            ctx.add_metadata(trades=100, symbol='XAUUSD')
    """
    
    def __init__(self, operation: str):
        self.operation = operation
        self.start_time = None
        self.metadata = {}
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        success = exc_type is None
        
        _metrics_store[self.operation].append({
            'timestamp': datetime.now().isoformat(),
            'duration': duration,
            'success': success,
            'error': str(exc_val) if exc_val else None,
            'metadata': self.metadata
        })
        
        if duration > 10:
            logger.warning(f"SLOW: {self.operation} took {duration:.2f}s")
        else:
            logger.info(f"{self.operation} took {duration:.2f}s")
        
        return False  # Don't suppress exceptions
    
    def add_metadata(self, **kwargs):
        """Add metadata to this operation's metrics."""
        self.metadata.update(kwargs)
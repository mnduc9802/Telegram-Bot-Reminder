import logging
from logging.handlers import MemoryHandler
from datetime import datetime, timedelta
from collections import deque
import time

class TimedMemoryHandler(MemoryHandler):
    def __init__(self, days_limit=30):
        self.log_buffer = deque(maxlen=10000)
        self.days_limit = days_limit
        super().__init__(capacity=1)

    def emit(self, record):
        record.created_dt = datetime.fromtimestamp(record.created)
        self.log_buffer.append(record)
        
        current_time = datetime.now()
        cutoff_date = current_time - timedelta(days=self.days_limit)
        
        while self.log_buffer and self.log_buffer[0].created_dt < cutoff_date:
            self.log_buffer.popleft()
        
        print(self.format(record))

    def get_buffer_size(self):
        return len(self.log_buffer)

    def get_oldest_log_date(self):
        if self.log_buffer:
            return self.log_buffer[0].created_dt
        return None

def test_logging():
    # Configure logger
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)
    
    # Create handler
    memory_handler = TimedMemoryHandler(days_limit=30)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    memory_handler.setFormatter(formatter)
    logger.addHandler(memory_handler)

    print("\n=== Starting logging test ===")

    # Test 1: Create logs for 35 days (exceeding 30-day limit)
    print("\nTest 1: Creating logs for 35 days...")
    base_time = datetime.now() - timedelta(days=35)
    
    for days in range(35):
        test_time = base_time + timedelta(days=days)
        # Create a record with custom timestamp
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_logging.py",
            lineno=1,
            msg=f"Log message for day {days + 1}",
            args=(),
            exc_info=None,
            func="test_function"
        )
        # Set the created timestamp directly
        record.created = test_time.timestamp()
        record.created_dt = test_time
        logger.handle(record)
        
    print(f"\nNumber of logs in buffer: {memory_handler.get_buffer_size()}")
    if memory_handler.get_oldest_log_date():
        print(f"Oldest log date: {memory_handler.get_oldest_log_date()}")
        print(f"Days from oldest log to now: {(datetime.now() - memory_handler.get_oldest_log_date()).days} days")

    # Test 2: Create new log to check old log cleanup
    print("\nTest 2: Creating new log...")
    logger.info("New log created")
    
    print(f"\nNumber of logs in buffer after adding new log: {memory_handler.get_buffer_size()}")
    if memory_handler.get_oldest_log_date():
        print(f"Oldest log date after adding new log: {memory_handler.get_oldest_log_date()}")
        print(f"Days from oldest log to now: {(datetime.now() - memory_handler.get_oldest_log_date()).days} days")

    print("\n=== Logging test completed ===")

if __name__ == "__main__":
    test_logging()
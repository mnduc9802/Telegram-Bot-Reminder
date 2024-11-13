import telebot
import logging
import sys
from datetime import datetime
import pytz
import time
from unittest.mock import Mock

# Cấu hình Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Mock bot để test
class MockBot:
    def __init__(self, fail_count=2):
        self.fail_count = fail_count
        self.current_attempt = 0
        
    def send_message(self, chat_id, message, parse_mode=None):
        self.current_attempt += 1
        if self.current_attempt <= self.fail_count:
            raise telebot.apihelper.ApiException("Simulated API error")
        return True

def send_message_with_retry(bot, chat_id, message, max_retries=3, retry_delay=5, parse_mode="HTML"):
    """
    Gửi tin nhắn với cơ chế retry
    - max_retries: số lần thử lại tối đa (mặc định 3 lần)
    - retry_delay: thời gian chờ giữa các lần thử lại tính bằng giây (đã giảm xuống 5s để test nhanh hơn)
    """
    attempt = 0
    last_error = None
    
    while attempt < max_retries:
        try:
            logger.info(f"Attempting to send message (attempt {attempt + 1}/{max_retries})")
            bot.send_message(chat_id, message, parse_mode=parse_mode)
            if attempt > 0:
                logger.info(f"Message sent successfully after {attempt + 1} attempts")
            return True
        except Exception as e:
            attempt += 1
            last_error = str(e)
            if attempt < max_retries:
                logger.warning(f"Attempt {attempt} failed: {last_error}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"All {max_retries} attempts failed. Last error: {last_error}")
    
    return False

def test_successful_after_retries():
    """Test 1: Thành công sau 2 lần thất bại"""
    logger.info("\n=== Test 1: Success after 2 failures ===")
    mock_bot = MockBot(fail_count=2)
    result = send_message_with_retry(
        bot=mock_bot,
        chat_id="test_chat",
        message="Test message",
        max_retries=3,
        retry_delay=5
    )
    assert result == True, "Should succeed on third attempt"
    logger.info("Test 1 passed: Message sent successfully after retries\n")

def test_all_attempts_fail():
    """Test 2: Thất bại tất cả các lần thử"""
    logger.info("\n=== Test 2: All attempts fail ===")
    mock_bot = MockBot(fail_count=5)  # Will fail more times than max_retries
    result = send_message_with_retry(
        bot=mock_bot,
        chat_id="test_chat",
        message="Test message",
        max_retries=3,
        retry_delay=5
    )
    assert result == False, "Should fail after all retries"
    logger.info("Test 2 passed: Properly handled all failures\n")

def test_success_first_try():
    """Test 3: Thành công ngay lần đầu"""
    logger.info("\n=== Test 3: Success on first try ===")
    mock_bot = MockBot(fail_count=0)
    result = send_message_with_retry(
        bot=mock_bot,
        chat_id="test_chat",
        message="Test message",
        max_retries=3,
        retry_delay=5
    )
    assert result == True, "Should succeed on first attempt"
    logger.info("Test 3 passed: Message sent successfully on first try\n")

if __name__ == "__main__":
    try:
        # Chạy các test cases
        test_successful_after_retries()
        test_all_attempts_fail()
        test_success_first_try()
        
        logger.info("All tests completed successfully!")
    except AssertionError as e:
        logger.error(f"Test failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during testing: {str(e)}")
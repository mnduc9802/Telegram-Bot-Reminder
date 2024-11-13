import telebot
from datetime import datetime, timedelta
import schedule
import time
import pytz
from dotenv import load_dotenv
import os
import logging
from logging.handlers import MemoryHandler
import sys
from collections import deque

class TimedMemoryHandler(MemoryHandler):
    def __init__(self, days_limit=30): # days_limit là số ngày
        self.log_buffer = deque(maxlen=10000)  # Giới hạn buffer size
        self.days_limit = days_limit
        super().__init__(capacity=1)

    def emit(self, record):
        record.created_dt = datetime.fromtimestamp(record.created)
        self.log_buffer.append(record)
        
        # Xóa log cũ hơn 30 ngày
        current_time = datetime.now()
        cutoff_date = current_time - timedelta(days=self.days_limit)
        
        while self.log_buffer and self.log_buffer[0].created_dt < cutoff_date:
            self.log_buffer.popleft()
        
        print(self.format(record))

# Cấu hình Logging với TimedMemoryHandler
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
memory_handler = TimedMemoryHandler(days_limit=30)
memory_handler.setFormatter(formatter)
logger.addHandler(memory_handler)

# Load biến môi trường từ file .env
load_dotenv()
# Thay YOUR_BOT_TOKEN bằng token bot của bạn từ BotFather
BOT_TOKEN = os.getenv('BOT_TOKEN')
# Thay CHAT_ID bằng ID của nhóm chat
CHAT_ID = os.getenv('CHAT_ID')
# Kiểm tra xem các biến môi trường có tồn tại không
if not BOT_TOKEN or not CHAT_ID:
    logger.error("Environment variables BOT_TOKEN or CHAT_ID not found")
    raise ValueError("Environment variables BOT_TOKEN or CHAT_ID not found")

# Khởi tạo bot
bot = telebot.TeleBot(BOT_TOKEN)
logger.info("Bot initialized successfully")

# Thiết lập múi giờ Việt Nam
vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')

#Hàm retry gửi tin nhắn khi bị lỗi
def send_message_with_retry(chat_id, message, max_retries=3, retry_delay=300, parse_mode="HTML"):
    """
    Gửi tin nhắn với cơ chế retry
    - max_retries: số lần thử lại tối đa (mặc định 3 lần)
    - retry_delay: thời gian chờ giữa các lần thử lại tính bằng giây (mặc định 300s = 5 phút)
    """
    attempt = 0
    last_error = None
    
    while attempt < max_retries:
        try:
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

def send_daily_reminder():
    current_time = datetime.now(vietnam_tz)
    # Chỉ gửi tin nhắn vào các ngày trong tuần (0 = thứ 2, 6 = chủ nhật)
    if current_time.weekday() < 5:  # Từ thứ 2 đến thứ 6
        daily_message = """<b>BÁO CÁO NGÀY:</b>
    + Làm báo cáo cá nhân cuối ngày và lên kế hoạch làm việc ngày mai."""
        
        success = send_message_with_retry(CHAT_ID, daily_message, parse_mode="HTML")
        if success:
            logger.info(f"Daily reminder sent successfully at {current_time}")
        else:
            logger.error("Failed to send daily reminder after all retries")

def send_weekly_reminder():
    sheet_url = "https://docs.google.com/spreadsheets/d/1BzyuvJw_xQZEcapfBpTAx2IXPEmlT6ONrh3t1odUBuU/edit?gid=224745787#gid=224745787"
    weekly_message = """<b>TỔNG HỢP & NỘP BÁO CÁO TUẦN:</b>
    + Các đầu việc đã hoàn thành.
    + Các đầu việc đang làm dở dang trong tuần.
    + Dự kiến đầu việc trong tuần sau.
    + Báo cáo trực tiếp trong nhóm (BA, FE, BE, Sys, K5 INTERN), riêng BA/TESTER K5 gửi vào mail của chị.
    + Ngoài ra các bạn nhớ update lịch làm việc thực tế trong tuần & đăng ký lịch làm việc tuần sau vào file <a href="{}">Lịch làm việc</a> nhé!""".format(sheet_url)
    
    success = send_message_with_retry(CHAT_ID, weekly_message, parse_mode="HTML")
    if success:
        current_time = datetime.now(vietnam_tz)
        logger.info(f"Weekly report reminder sent successfully at {current_time}")
    else:
        logger.error("Failed to send weekly reminder after all retries")

def send_monthly_reminder():
    # Lấy ngày hiện tại theo múi giờ Việt Nam
    current_time = datetime.now(vietnam_tz)
    
    # Chỉ gửi tin nhắn vào ngày mùng 1
    if current_time.day == 1:
        sheet_url = "https://docs.google.com/spreadsheets/d/1BzyuvJw_xQZEcapfBpTAx2IXPEmlT6ONrh3t1odUBuU/edit?gid=224745787#gid=224745787"
        monthly_message = """<b>BÁO CÁO THÁNG:</b>
    + Team Dev tổng hợp các đầu việc đã hoàn thành trong tháng vào file để tính point.
    + Team BA tổng hợp các đầu việc đã làm trong tháng vào form báo cáo mới.
    + <b>Deadline chung 12h ngày mùng 5 đầu tháng.</b>
    + Ngoài ra các bạn nhớ update lịch làm việc thực tế trong tháng & đăng ký lịch làm việc tháng mới vào file <a href="{}">Lịch làm việc</a> nhé!""".format(sheet_url)
        
        success = send_message_with_retry(CHAT_ID, monthly_message, parse_mode="HTML")
        if success:
            logger.info(f"Monthly report reminder sent successfully at {current_time}")
        else:
            logger.error("Failed to send monthly reminder after all retries")
    else:
        logger.info(f"Skipping monthly reminder - not first day of month (current day: {current_time.day})")

def setup_schedule():
    # Lên lịch gửi tin nhắn hàng ngày lúc 17:00
    schedule.every().day.at("17:00").do(send_daily_reminder)
    logger.info("Daily reminder scheduled for 17:00")
    # Lên lịch gửi tin nhắn báo cáo tuần vào 10:00 sáng thứ 7
    schedule.every().saturday.at("10:00").do(send_weekly_reminder)
    logger.info("Weekly reminder scheduled for Saturday 10:00")
    # Lên lịch kiểm tra và gửi tin nhắn báo cáo tháng vào 10:00 sáng hàng ngày
    schedule.every().day.at("10:00").do(send_monthly_reminder)
    logger.info("Monthly reminder check scheduled for 10:00 daily")
    
    logger.info("Bot startup completed - All schedules initialized")

    while True:
        try:
            schedule.run_pending()
            time.sleep(15)  # Check every 15 seconds
        except Exception as e:
            logger.error(f"Schedule execution error: {str(e)}")

if __name__ == "__main__":
    try:
        logger.info("Starting Telegram reminder bot...")
        setup_schedule()
    except Exception as e:
        logger.error(f"Bot startup failed: {str(e)}")
        sys.exit(1)

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

class Logger:
    def __init__(self):
        # Cấu hình Logging với TimedMemoryHandler
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        memory_handler = TimedMemoryHandler(days_limit=30)
        memory_handler.setFormatter(formatter)
        self.logger.addHandler(memory_handler)

class DateFormatter:
    @staticmethod
    def get_vietnamese_weekday(date):
        weekdays = {
            0: "THỨ HAI",
            1: "THỨ BA", 
            2: "THỨ TƯ",
            3: "THỨ NĂM",
            4: "THỨ SÁU",
            5: "THỨ BẢY",
            6: "CHỦ NHẬT"
        }
        return weekdays[date.weekday()]

    @staticmethod
    def get_week_number(date):
        # Lấy ngày đầu tiên của tháng
        first_day = date.replace(day=1)
        # Điều chỉnh để tuần đầu tiên bắt đầu từ ngày 1
        week_number = (date.day - 1) // 7 + 1
        return week_number

    @staticmethod
    def format_date(date):
        return date.strftime("%d/%m/%Y")

class TelegramBot:
    def __init__(self):
        self.logger = Logger().logger
        # Thiết lập múi giờ Việt Nam
        self.vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        self.load_environment()
        # Khởi tạo bot
        self.bot = telebot.TeleBot(self.bot_token)
        self.sheet_url = "https://docs.google.com/spreadsheets/d/1BzyuvJw_xQZEcapfBpTAx2IXPEmlT6ONrh3t1odUBuU/edit?gid=224745787#gid=224745787"
        self.logger.info("Bot initialized successfully")

    def load_environment(self):
        # Load biến môi trường từ file .env
        load_dotenv()
        # Thay YOUR_BOT_TOKEN bằng token bot của bạn từ BotFather
        self.bot_token = os.getenv('BOT_TOKEN')
        # Thay CHAT_ID bằng ID của nhóm chat
        self.chat_id = os.getenv('CHAT_ID')
        # Kiểm tra xem các biến môi trường có tồn tại không
        if not self.bot_token or not self.chat_id:
            self.logger.error("Environment variables BOT_TOKEN or CHAT_ID not found")
            raise ValueError("Environment variables BOT_TOKEN or CHAT_ID not found")

    #Hàm retry gửi tin nhắn khi bị lỗi
    def send_message_with_retry(self, message, max_retries=3, retry_delay=300, parse_mode="HTML"):
        """
        Gửi tin nhắn với cơ chế retry
        - max_retries: số lần thử lại tối đa (mặc định 3 lần)
        - retry_delay: thời gian chờ giữa các lần thử lại tính bằng giây (mặc định 300s = 5 phút)
        """
        attempt = 0
        last_error = None
        
        while attempt < max_retries:
            try:
                self.bot.send_message(self.chat_id, message, parse_mode=parse_mode)
                if attempt > 0:
                    self.logger.info(f"Message sent successfully after {attempt + 1} attempts")
                return True
            except Exception as e:
                attempt += 1
                last_error = str(e)
                if attempt < max_retries:
                    self.logger.warning(f"Attempt {attempt} failed: {last_error}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    self.logger.error(f"All {max_retries} attempts failed. Last error: {last_error}")
        
        return False

class ReminderService:
    def __init__(self, bot: TelegramBot):
        self.bot = bot
        self.date_formatter = DateFormatter()

    #Gửi thông báo ngày
    def send_daily_reminder(self):
        current_time = datetime.now(self.bot.vietnam_tz)
        if current_time.weekday() < 5:  # Từ thứ 2 đến thứ 6
            weekday = self.date_formatter.get_vietnamese_weekday(current_time)
            date_str = self.date_formatter.format_date(current_time)
            
            daily_message = f"""<b>BÁO CÁO NGÀY {weekday}, {date_str}:</b>
        + Làm báo cáo cá nhân cuối ngày và lên kế hoạch làm việc ngày mai."""
            
            success = self.bot.send_message_with_retry(daily_message)
            if success:
                self.bot.logger.info(f"Daily reminder sent successfully at {current_time}")
            else:
                self.bot.logger.error("Failed to send daily reminder after all retries")

    #Gửi thông báo tuần
    def send_weekly_reminder(self):
        current_time = datetime.now(self.bot.vietnam_tz)
        week_number = self.date_formatter.get_week_number(current_time)
        month = current_time.strftime("%m/%Y")
        
        weekly_message = f"""<b>TỔNG HỢP & NỘP BÁO CÁO TUẦN {week_number}, THÁNG {month}:</b>
        + Các đầu việc đã hoàn thành.
        + Các đầu việc đang làm dở dang trong tuần.
        + Dự kiến đầu việc trong tuần sau.
        + Báo cáo trực tiếp trong nhóm (BA, FE, BE, Sys, K5 INTERN), riêng BA/TESTER K5 gửi vào mail của chị.
        + Ngoài ra các bạn nhớ update lịch làm việc thực tế trong tuần & đăng ký lịch làm việc tuần sau vào file <a href="{self.bot.sheet_url}">Lịch làm việc</a> nhé!"""
        
        success = self.bot.send_message_with_retry(weekly_message)
        if success:
            self.bot.logger.info(f"Weekly report reminder sent successfully at {current_time}")
        else:
            self.bot.logger.error("Failed to send weekly reminder after all retries")

    #Gửi thông báo tháng
    def send_monthly_reminder(self):
        current_time = datetime.now(self.bot.vietnam_tz)
        
        if current_time.day == 1:
            # Tính toán tháng trước
            if current_time.month == 1:
                previous_month = 12
                previous_year = current_time.year - 1
            else:
                previous_month = current_time.month - 1
                previous_year = current_time.year
                
            month_str = f"{previous_month:02d}/{previous_year}"
            
            monthly_message = f"""<b>BÁO CÁO THÁNG {month_str}:</b>
        + Team Dev tổng hợp các đầu việc đã hoàn thành trong tháng vào file để tính point.
        + Team BA tổng hợp các đầu việc đã làm trong tháng vào form báo cáo mới.
        + <b>Deadline chung 12h ngày mùng 5 đầu tháng.</b>
        + Ngoài ra các bạn nhớ update lịch làm việc thực tế trong tháng & đăng ký lịch làm việc tháng mới vào file <a href="{self.bot.sheet_url}">Lịch làm việc</a> nhé!"""
            
            success = self.bot.send_message_with_retry(monthly_message)
            if success:
                self.bot.logger.info(f"Monthly report reminder sent successfully at {current_time}")
            else:
                self.bot.logger.error("Failed to send monthly reminder after all retries")
        else:
            self.bot.logger.info(f"Skipping monthly reminder - not first day of month (current day: {current_time.day})")

class ScheduleManager:
    def __init__(self, reminder_service: ReminderService):
        self.reminder_service = reminder_service
        self.logger = reminder_service.bot.logger

    def setup_schedule(self):
        # Lên lịch gửi tin nhắn hàng ngày lúc 17:00
        schedule.every().day.at("17:00").do(self.reminder_service.send_daily_reminder)
        self.logger.info("Daily reminder scheduled for 17:00")
        
        # Lên lịch gửi tin nhắn báo cáo tuần vào 10:00 sáng thứ 7
        schedule.every().saturday.at("10:00").do(self.reminder_service.send_weekly_reminder)
        self.logger.info("Weekly reminder scheduled for Saturday 10:00")
        
        # Lên lịch kiểm tra và gửi tin nhắn báo cáo tháng vào 10:00 sáng hàng ngày
        schedule.every().day.at("10:00").do(self.reminder_service.send_monthly_reminder)
        self.logger.info("Monthly reminder check scheduled for 10:00 daily")
        
        self.logger.info("Bot startup completed - All schedules initialized")

    def run(self):
        while True:
            try:
                schedule.run_pending()
                time.sleep(20)  # Check every 20 seconds
            except Exception as e:
                self.logger.error(f"Schedule execution error: {str(e)}")

def main():
    try:
        bot = TelegramBot()
        reminder_service = ReminderService(bot)
        scheduler = ScheduleManager(reminder_service)
        
        bot.logger.info("Starting Telegram reminder bot...")
        scheduler.setup_schedule()
        scheduler.run()
    except Exception as e:
        bot.logger.error(f"Bot startup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
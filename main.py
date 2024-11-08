import telebot
from datetime import datetime
import schedule
import time
import pytz
from dotenv import load_dotenv
import os

# Load biến môi trường từ file .env
load_dotenv()
# Thay YOUR_BOT_TOKEN bằng token bot của bạn từ BotFather
BOT_TOKEN = os.getenv('BOT_TOKEN')
# Thay CHAT_ID bằng ID của nhóm chat
CHAT_ID = os.getenv('CHAT_ID')
# Kiểm tra xem các biến môi trường có tồn tại không
if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("Không tìm thấy BOT_TOKEN hoặc CHAT_ID trong biến môi trường")

# Khởi tạo bot
bot = telebot.TeleBot(BOT_TOKEN)

# Thiết lập múi giờ Việt Nam
vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')

def send_daily_reminder():
    current_time = datetime.now(vietnam_tz)
    # Chỉ gửi tin nhắn vào các ngày trong tuần (0 = thứ 2, 6 = chủ nhật)
    if current_time.weekday() < 5:  # Từ thứ 2 đến thứ 6
        daily_message = """<b>BÁO CÁO NGÀY:</b>
    + Làm báo cáo cá nhân cuối ngày và lên kế hoạch làm việc ngày mai."""
        try:
            bot.send_message(CHAT_ID, daily_message, parse_mode="HTML")
            print(f"Đã gửi lời nhắc hàng ngày vào lúc {current_time}")
        except Exception as e:
            print(f"Lỗi khi gửi tin nhắn: {e}")

def send_weekly_reminder():
    sheet_url = "https://docs.google.com/spreadsheets/d/1BzyuvJw_xQZEcapfBpTAx2IXPEmlT6ONrh3t1odUBuU/edit?gid=224745787#gid=224745787"
    weekly_message = """<b>TỔNG HỢP & NỘP BÁO CÁO TUẦN:</b>
    + Các đầu việc đã hoàn thành.
    + Các đầu việc đang làm dở dang trong tuần.
    + Dự kiến đầu việc trong tuần sau.
    + Báo cáo trực tiếp trong nhóm (BA, FE, BE, Sys, K5 INTERN), riêng BA/TESTER K5 gửi vào mail của chị.
    + Ngoài ra các bạn nhớ update lịch làm việc thực tế trong tuần & đăng ký lịch làm việc tuần sau vào file <a href="{}">Lịch làm việc</a> nhé!""".format(sheet_url)
    
    try:
        # Sử dụng parse_mode="HTML" để hỗ trợ định dạng markdown trong tin nhắn
        bot.send_message(CHAT_ID, weekly_message, parse_mode="HTML")
        current_time = datetime.now(vietnam_tz)
        print(f"Đã gửi lời nhắc báo cáo tuần vào lúc {current_time}")
    except Exception as e:
        print(f"Lỗi khi gửi tin nhắn: {e}")

def send_monthly_reminder():
    # Lấy ngày hiện tại theo múi giờ Việt Nam
    current_time = datetime.now(vietnam_tz)
    # Kiểm tra xem có phải là ngày mùng 1 không
    if current_time.day == 1:
        sheet_url = "https://docs.google.com/spreadsheets/d/1BzyuvJw_xQZEcapfBpTAx2IXPEmlT6ONrh3t1odUBuU/edit?gid=224745787#gid=224745787"
        monthly_message = """<b>BÁO CÁO THÁNG:</b>
    + Team Dev tổng hợp các đầu việc đã hoàn thành trong tháng vào file để tính point.
    + Team BA tổng hợp các đầu việc đã làm trong tháng vào form báo cáo mới.
    + <b>Deadline chung 12h ngày mùng 5 đầu tháng.</b>
    + Ngoài ra các bạn nhớ update lịch làm việc thực tế trong tháng & đăng ký lịch làm việc tháng mới vào file <a href="{}">Lịch làm việc</a> nhé!""".format(sheet_url)
        
        try:
            # Sử dụng parse_mode="HTML" để hỗ trợ định dạng markdown trong tin nhắn
            bot.send_message(CHAT_ID, monthly_message, parse_mode="HTML")
            print(f"Đã gửi lời nhắc báo cáo tháng vào lúc {current_time}")
        except Exception as e:
            print(f"Lỗi khi gửi tin nhắn: {e}")

def setup_schedule():
    # Lên lịch gửi tin nhắn hàng ngày lúc 17:00
    schedule.every().day.at("17:00").do(send_daily_reminder)
    # Lên lịch gửi tin nhắn báo cáo tuần vào 10:00 sáng thứ 7
    schedule.every().saturday.at("10:00").do(send_weekly_reminder)
    # Lên lịch kiểm tra và gửi tin nhắn báo cáo tháng vào 10:00 sáng hàng ngày
    schedule.every().day.at("10:00").do(send_monthly_reminder)
    
    print("Bot đã được khởi động và lên lịch...")

    while True:
        schedule.run_pending()
        time.sleep(30)  # Kiểm tra mỗi 30s

if __name__ == "__main__":
    try:
        setup_schedule()
    except Exception as e:
        print(f"Lỗi khởi động bot: {e}")
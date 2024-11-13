# :arrow_down: ENGLISH BELOW :arrow_down:

# TIẾNG VIỆT
# 🤖Telegram Reminder Bot by mnduc9802
> Một bot Telegram đơn giản để tự động gửi các nhắc nhở về báo cáo công việc theo lịch định sẵn cho nhóm làm việc, được tạo ra bởi @mnduc9802

## 📋 Mục lục 
- Tính năng
- Cài đặt
- Cấu hình môi trường
- Đóng góp
- Cảm ơn

## ✨ Tính năng
- 📅 Nhắc nhở báo cáo hàng ngày (17:00 các ngày trong tuần)
- 📊 Nhắc nhở báo cáo tuần (10:00 sáng thứ 7)
- 📈 Nhắc nhở báo cáo tháng (10:00 sáng ngày mùng 1 hàng tháng)
- 🔁 Tự động thử lại khi gửi tin nhắn thất bại
- 📝 Ghi log đầy đủ cho việc giám sát hoạt động

## 🚀 Cài đặt
### Yêu cầu tiên quyết
- Python 3.6 trở lên
- Docker (tùy chọn)

## Các bước cài đặt
1. Clone repository:
```
git clone [url-repository]
cd telegram-reminder-bot
```
2. Cài đặt các thư viện cần thiết:
`pip install -r requirements.txt`
3. Tạo file `.env` với nội dung sau:
```
BOT_TOKEN = ********
CHAT_ID = ********
```

## Cấu hình môi trường

### Lấy Bot Token
1. Truy cập @BotFather trên Telegram
2. Tạo bot mới bằng lệnh /newbot
3. Lưu lại token được cấp
### Lấy Chat ID
1. Thêm bot vào nhóm chat cần gửi nhắc nhở
2. Sử dụng Telegram WEB để xem Chat ID

## Chạy ứng dụng
### Chạy trực tiếp
`python main.py`

### Chạy bằng Docker
1. Build image:
`docker build -t telegram-reminder-bot .`
2. Chạy container:
`docker run -d telegram-reminder-bot`

## 👥 Đóng góp
Chào đón mọi đóng góp! Vui lòng gửi Pull Request.

## 🙏 Cảm ơn
- pyTelegramBotAPI: Tương tác với Telegram Bot API
- schedule: Lên lịch các tác vụ
- pytz: Xử lý múi giờ
- python-dotenv: Đọc biến môi trường từ file .env
- logging: Ghi log hoạt động

---
# ENGLISH
# 🤖Telegram Deploy Bot by mnduc9802
> A simple Telegram bot to automatically send work report reminders according to preset schedules for work groups, created by @mnduc9802

## 📋 Table of Contents
- Important Settings
- Introduction
- Architecture
- Features
- Commands
- Installation
- Configuration
- Usage
- Notes

## ✨ Features
- 📅 Daily report reminders (17:00 on weekdays)
- 📊 Weekly report reminders (10:00 AM on Saturdays)
- 📈 Monthly report reminders (10:00 AM on the 1st day of each month)
- 🔁 Automatic retry for failed message deliveries
- 📝 Comprehensive logging for activity monitoring

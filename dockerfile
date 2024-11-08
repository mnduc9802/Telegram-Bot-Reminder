# Sử dụng image Python phiên bản 3.9
FROM python:3.9

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép tệp tin từ thư mục hiện tại sang thư mục trong container
COPY . .

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir \
    pyTelegramBotAPI \
    datetime \
    schedule \
    pytz \
    python-dotenv

# Chạy ứng dụng khi container được khởi chạy
CMD ["python", "main.py"]
# Sử dụng image Python phiên bản 3.9
FROM python:3.9

# Cài đặt tzdata để hỗ trợ timezone
RUN apt-get update && apt-get install -y tzdata

# Thiết lập timezone cho container
ENV TZ=Asia/Ho_Chi_Minh
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy requirements.txt trước
COPY requirements.txt .

# Cài đặt các thư viện từ requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code source
COPY . .

# Chạy ứng dụng với log
CMD ["python", "-u", "main.py"]
# Python 3.10 이미지를 기반으로 함
FROM python:3.10

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 패키지 설치
RUN apt-get update \
    && apt-get install -y g++ default-jdk python3-dev python3-pip curl \
    && pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Java 버전 출력
RUN java -version

# 소스 코드를 Docker 컨테이너 내에 복사
COPY . .

# 명령어 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

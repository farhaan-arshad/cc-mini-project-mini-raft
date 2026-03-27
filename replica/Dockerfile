# Docker config for replica (shared by all 3)
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001
EXPOSE 8002
EXPOSE 8003

CMD ["uvicorn", "replica:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
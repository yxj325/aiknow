# 构建阶段
FROM python:3.10-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 运行阶段
FROM python:3.10-slim

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

# 数据目录
RUN mkdir -p data/chroma data/cache/embeddings data/uploads logs
VOLUME ["/app/data", "/app/logs"]

EXPOSE 8000

ENV AIKNOW_CONFIG=/app/config.yaml
ENV PYTHONPATH=/app

CMD ["python", "-m", "app.api.main"]

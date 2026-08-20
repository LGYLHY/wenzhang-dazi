# 文案搭子 · 后端镜像
# 隐私设计：容器不持久化原图/人脸，仅持久化 SQLite + Chroma 向量
FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# 先装依赖（利用层缓存）
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app

# 数据卷：SQLite 元数据 + Chroma 向量（不含图片）
VOLUME ["/app/data"]

EXPOSE 8000

# 生产建议：--workers 1（Chroma 内存态简单起见）
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

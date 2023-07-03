# Use Python 3.10
ARG BASE_IMAGE="python:3.10-bullseye"
FROM ${BASE_IMAGE}
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    apt-get update ; \
    apt-get upgrade -y ; \
    apt-get install -y --no-install-recommends git build-essential g++ libgomp1 ffmpeg python3 python3-pip python3-dev curl && \
    rm -rf /var/lib/apt/lists/*
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip install -U pip setuptools
ENV UVICORN_WORKERS=4
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "Main.py", "--server.headless", "true"]

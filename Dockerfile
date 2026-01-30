FROM python:3.12-slim
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y \
    build-essential libsndfile1 mecab libmecab-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN uv venv .venv --python 3.12
RUN uv pip install --timeout 120 -e .
RUN uv pip install soxr
RUN uv run python -m unidic download
RUN uv run python -c "import nltk; nltk.download('averaged_perceptron_tagger_eng')"
RUN uv run python melo/init_downloads.py

ENV PYTHONUNBUFFERED=1

EXPOSE 8080 50051 8888
CMD ["uv", "run", "python", "./melo/openai_api.py", "--host", "0.0.0.0", "--port", "8080", "--grpc-port", "50051", "--ui-port", "8888"]

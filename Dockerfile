FROM python:3.9-slim
WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y \
    build-essential libsndfile1 mecab libmecab-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install --timeout 120 -e .
RUN pip install soxr gradio==4.19.2
RUN python -m unidic download
RUN python -c "import nltk; nltk.download('averaged_perceptron_tagger_eng')"
RUN python melo/init_downloads.py

ENV PYTHONUNBUFFERED=1

EXPOSE 8080 50051
CMD ["python", "./melo/openai_api.py", "--host", "0.0.0.0", "--port", "8080", "--grpc-port", "50051"]

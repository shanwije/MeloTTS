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

EXPOSE 8888
CMD ["python", "./melo/app.py", "--host", "0.0.0.0", "--port", "8888"]

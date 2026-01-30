<div align="center">
  <div>&nbsp;</div>
  <img src="logo.png" width="300"/> <br>
  <a href="https://trendshift.io/repositories/8133" target="_blank"><img src="https://trendshift.io/api/badge/repositories/8133" alt="myshell-ai%2FMeloTTS | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
</div>

## Introduction
MeloTTS is a **high-quality multi-lingual** text-to-speech library by [MIT](https://www.mit.edu/) and [MyShell.ai](https://myshell.ai). Supported languages include:

| Language | Example |
| --- | --- |
| English (American)    | [Link](https://myshell-public-repo-host.s3.amazonaws.com/myshellttsbase/examples/en/EN-US/speed_1.0/sent_000.wav) |
| English (British)     | [Link](https://myshell-public-repo-host.s3.amazonaws.com/myshellttsbase/examples/en/EN-BR/speed_1.0/sent_000.wav) |
| English (Indian)      | [Link](https://myshell-public-repo-host.s3.amazonaws.com/myshellttsbase/examples/en/EN_INDIA/speed_1.0/sent_000.wav) |
| English (Australian)  | [Link](https://myshell-public-repo-host.s3.amazonaws.com/myshellttsbase/examples/en/EN-AU/speed_1.0/sent_000.wav) |
| English (Default)     | [Link](https://myshell-public-repo-host.s3.amazonaws.com/myshellttsbase/examples/en/EN-Default/speed_1.0/sent_000.wav) |
| Spanish               | [Link](https://myshell-public-repo-host.s3.amazonaws.com/myshellttsbase/examples/es/ES/speed_1.0/sent_000.wav) |
| French                | [Link](https://myshell-public-repo-host.s3.amazonaws.com/myshellttsbase/examples/fr/FR/speed_1.0/sent_000.wav) |
| Chinese (mix EN)      | [Link](https://myshell-public-repo-host.s3.amazonaws.com/myshellttsbase/examples/zh/ZH/speed_1.0/sent_008.wav) |
| Japanese              | [Link](https://myshell-public-repo-host.s3.amazonaws.com/myshellttsbase/examples/jp/JP/speed_1.0/sent_000.wav) |
| Korean                | [Link](https://myshell-public-repo-host.s3.amazonaws.com/myshellttsbase/examples/kr/KR/speed_1.0/sent_000.wav) |

Some other features include:
- The Chinese speaker supports `mixed Chinese and English`.
- Fast enough for `CPU real-time inference`.

## Usage
- [Use without Installation](docs/quick_use.md)
- [Install and Use Locally](docs/install.md)
- [Training on Custom Dataset](docs/training.md)

The Python API and model cards can be found in [this repo](https://github.com/myshell-ai/MeloTTS/blob/main/docs/install.md#python-api) or on [HuggingFace](https://huggingface.co/myshell-ai).

## Server Deployment

MeloTTS exposes two server interfaces:

| Interface | Port | Use Case |
|-----------|------|----------|
| OpenAI-compatible REST API | 8080 | LiteLLM proxy, standard HTTP clients |
| gRPC streaming | 50051 | Low-latency sentence-level audio streaming |

### Docker

```bash
docker build -t melotts .
docker run -p 8080:8080 -p 50051:50051 melotts
```

### Local

```bash
make setup
make api       # starts both REST (8080) + gRPC (50051)
make grpc      # starts gRPC server only
```

### REST API (OpenAI-compatible)

```bash
curl http://localhost:8080/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello world", "voice": "en-us"}' \
  --output test.wav
```

Available endpoints:
- `POST /v1/audio/speech` — synthesize speech
- `GET /v1/audio/voices` — list available voices
- `GET /v1/models` — list models
- `GET /health` — health check

### gRPC Streaming

The gRPC server streams audio chunks per sentence for low-latency playback. Proto definition: `melo/proto/tts.proto`

```python
import grpc
from melo.proto import tts_pb2, tts_pb2_grpc

channel = grpc.insecure_channel("localhost:50051")
stub = tts_pb2_grpc.MeloTTSStub(channel)

request = tts_pb2.SpeechRequest(text="Hello world. How are you?", voice="en-us", speed=1.0)
for chunk in stub.SynthesizeSpeechStream(request):
    with open(f"chunk_{chunk.chunk_index}.wav", "wb") as f:
        f.write(chunk.audio_data)
```

### LiteLLM Proxy Configuration

To use MeloTTS as a TTS backend via LiteLLM:

```yaml
model_list:
  - model_name: melo-tts
    litellm_params:
      model: openai/melo-tts
      api_base: http://<HOST>:8080/v1
      api_key: "placeholder"
```

### AWS Deployment

**EC2 (recommended for simplicity):**
- Instance type: `c5.xlarge` or larger (CPU inference)
- Security group: open ports 8080 (REST) and 50051 (gRPC)
- Run via Docker or systemd

```bash
docker run -d --restart unless-stopped \
  -p 8080:8080 -p 50051:50051 \
  melotts
```

**ECS/Fargate alternative:**
- Use ALB for REST traffic (port 8080)
- Use NLB for gRPC traffic (port 50051, HTTP/2)
- Task definition: 2 vCPU, 4GB memory minimum

**Contributing**

If you find this work useful, please consider contributing to this repo.

- Many thanks to [@fakerybakery](https://github.com/fakerybakery) for adding the Web UI and CLI part.

## Authors

- [Wenliang Zhao](https://wl-zhao.github.io) at Tsinghua University
- [Xumin Yu](https://yuxumin.github.io) at Tsinghua University
- [Zengyi Qin](https://www.qinzy.tech) (project lead) at MIT and MyShell

**Citation**
```
@software{zhao2024melo,
  author={Zhao, Wenliang and Yu, Xumin and Qin, Zengyi},
  title = {MeloTTS: High-quality Multi-lingual Multi-accent Text-to-Speech},
  url = {https://github.com/myshell-ai/MeloTTS},
  year = {2023}
}
```

## License

This library is under MIT License, which means it is free for both commercial and non-commercial use.

## Acknowledgements

This implementation is based on [TTS](https://github.com/coqui-ai/TTS), [VITS](https://github.com/jaywalnut310/vits), [VITS2](https://github.com/daniilrobnikov/vits2) and [Bert-VITS2](https://github.com/fishaudio/Bert-VITS2). We appreciate their awesome work.

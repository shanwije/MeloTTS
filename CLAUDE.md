# Project Status

## Architecture
- **Shared TTS engine** (`melo/tts_engine.py`): loads EN + ZH models once, exposes `synthesize()` and `synthesize_stream()` used by both servers
- **REST API** (`melo/openai_api.py`): OpenAI-compatible `/v1/audio/speech` endpoint on port 8080, orchestrates all servers
- **gRPC server** (`melo/grpc_server.py`): sentence-level streaming via `SynthesizeSpeechStream` on port 50051
- **Gradio UI** (`melo/app.py`): web UI for testing TTS on port 8888
- **Proto definition** (`melo/proto/tts.proto`): defines `MeloTTS` service with `SynthesizeSpeechStream` and `ListVoices` RPCs

## Tooling
- Uses **uv** for package management (venv creation, pip installs, running scripts)
- Python 3.12

## Key Make targets
- `make setup` — install deps via uv and download models
- `make serve` — start all servers (REST 8080 + gRPC 50051 + UI 8888)
- `make api` — start REST + gRPC only
- `make ui` — start Gradio UI only
- `make grpc` — start gRPC server only
- `make proto` — regenerate protobuf Python code

## Last completed task
Migrated to uv for project management:
- Makefile uses `uv venv`, `uv pip install`, `uv run` instead of raw python/pip
- Dockerfile uses `ghcr.io/astral-sh/uv:latest` multi-stage copy, Python 3.12 base

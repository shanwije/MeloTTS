# Project Status

## Architecture
- **Shared TTS engine** (`melo/tts_engine.py`): loads EN + ZH models once, exposes `synthesize()` and `synthesize_stream()` used by both servers
- **REST API** (`melo/openai_api.py`): OpenAI-compatible `/v1/audio/speech` endpoint on port 8080, also starts gRPC server
- **gRPC server** (`melo/grpc_server.py`): sentence-level streaming via `SynthesizeSpeechStream` on port 50051
- **Proto definition** (`melo/proto/tts.proto`): defines `MeloTTS` service with `SynthesizeSpeechStream` and `ListVoices` RPCs

## Key Make targets
- `make setup` — install deps and download models
- `make api` — start both REST + gRPC servers
- `make grpc` — start gRPC server only
- `make proto` — regenerate protobuf Python code

## Last completed task
gRPC streaming TTS + OpenAI REST API + LiteLLM integration:
- Created shared `tts_engine.py` with thread-safe model access
- Created `melo/proto/tts.proto` and generated Python stubs
- Created `melo/grpc_server.py` with sentence-level audio streaming
- Refactored `openai_api.py` to use shared engine and co-launch gRPC
- Updated Dockerfile (exposes 8080 + 50051), requirements.txt (grpcio), Makefile, README

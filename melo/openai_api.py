import io
import logging
import threading

import click
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from melo import tts_engine

logger = logging.getLogger(__name__)
app = FastAPI()


class SpeechRequest(BaseModel):
    model: str = "melo-tts"
    input: str
    voice: str = "en-us"
    response_format: Optional[str] = "wav"
    speed: Optional[float] = 1.0


@app.post("/v1/audio/speech")
async def create_speech(request: SpeechRequest):
    voice_key = request.voice.lower()
    voices = tts_engine.get_voices()

    if voice_key not in voices:
        return Response(
            content=f'{{"error": "Unknown voice: {request.voice}. Available: {voices}"}}',
            status_code=400,
            media_type="application/json",
        )

    fmt = request.response_format or "wav"
    audio_bytes = tts_engine.synthesize(request.input, voice_key, request.speed, fmt)

    media_types = {
        "wav": "audio/wav",
        "mp3": "audio/mpeg",
        "flac": "audio/flac",
        "ogg": "audio/ogg",
    }
    media_type = media_types.get(fmt, "audio/wav")
    return StreamingResponse(io.BytesIO(audio_bytes), media_type=media_type)


@app.get("/v1/models")
async def list_models():
    return {
        "data": [{"id": "melo-tts", "object": "model", "owned_by": "melotts"}]
    }


@app.get("/v1/audio/voices")
async def list_voices():
    return {"voices": tts_engine.get_voices()}


@app.get("/health")
async def health():
    return {"status": "ok"}


@click.command()
@click.option("--host", "-h", default="0.0.0.0")
@click.option("--port", "-p", type=int, default=8080)
@click.option("--device", "-d", default="auto")
@click.option("--grpc-port", type=int, default=50051, help="gRPC server port (0 to disable)")
@click.option("--ui-port", type=int, default=0, help="Gradio UI port (0 to disable)")
def main(host, port, device, grpc_port, ui_port):
    logging.basicConfig(level=logging.INFO)
    tts_engine.init_models(device)

    grpc_server = None
    if grpc_port:
        from melo.grpc_server import serve as grpc_serve
        grpc_server = grpc_serve(grpc_port)
        logger.info("gRPC server started on port %d", grpc_port)

    if ui_port:
        from melo.app import launch_ui
        launch_ui(host=host, port=ui_port)
        logger.info("Gradio UI started on port %d", ui_port)

    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()

import logging
from concurrent import futures

import click
import grpc

from melo.proto import tts_pb2, tts_pb2_grpc
from melo import tts_engine

logger = logging.getLogger(__name__)


class MeloTTSServicer(tts_pb2_grpc.MeloTTSServicer):

    def SynthesizeSpeechStream(self, request, context):
        voice = request.voice or "en-us"
        speed = request.speed or 1.0
        text = request.text

        if not text:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("text is required")
            return

        try:
            for audio, sample_rate, chunk_index, is_last in tts_engine.synthesize_stream(
                text, voice, speed
            ):
                wav_bytes = tts_engine.audio_to_wav_bytes(audio, sample_rate)
                yield tts_pb2.AudioChunk(
                    audio_data=wav_bytes,
                    sample_rate=sample_rate,
                    chunk_index=chunk_index,
                    is_last=is_last,
                )
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))

    def ListVoices(self, request, context):
        voices = []
        for voice_key in tts_engine.get_voices():
            lang = tts_engine._voice_to_language.get(voice_key, "")
            voices.append(tts_pb2.Voice(name=voice_key, language=lang))
        return tts_pb2.VoiceList(voices=voices)


def serve(port: int = 50051, max_workers: int = 4):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    tts_pb2_grpc.add_MeloTTSServicer_to_server(MeloTTSServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    logger.info("gRPC server started on port %d", port)
    return server


@click.command()
@click.option("--port", "-p", type=int, default=50051)
@click.option("--device", "-d", default="auto")
def main(port, device):
    logging.basicConfig(level=logging.INFO)
    tts_engine.init_models(device)
    server = serve(port)
    logger.info("gRPC server listening on port %d", port)
    server.wait_for_termination()


if __name__ == "__main__":
    main()

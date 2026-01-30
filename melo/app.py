import gradio as gr
import io
import click

from melo import tts_engine

speed = 1.0

default_text_dict = {
    'EN': 'The field of text-to-speech has seen rapid development recently.',
    'ZH': 'text-to-speech 领域近年来发展迅速',
}


def synthesize(speaker, text, speed, language, progress=gr.Progress()):
    models = tts_engine.get_models()
    model = models[language]
    bio = io.BytesIO()
    model.tts_to_file(
        text, model.hps.data.spk2id[speaker], bio,
        speed=speed, pbar=progress.tqdm, format='wav',
    )
    return bio.getvalue()


def load_speakers(language, text):
    models = tts_engine.get_models()
    if text in list(default_text_dict.values()):
        newtext = default_text_dict[language]
    else:
        newtext = text
    speakers = list(models[language].hps.data.spk2id.keys())
    return gr.update(value=speakers[0], choices=speakers), newtext


def create_ui():
    models = tts_engine.get_models()
    speaker_ids = models['EN'].hps.data.spk2id

    with gr.Blocks() as demo:
        gr.Markdown('# MeloTTS WebUI\n\nA WebUI for MeloTTS.')
        with gr.Group():
            speaker = gr.Dropdown(speaker_ids.keys(), interactive=True, value='EN-US', label='Speaker')
            language = gr.Radio(['EN', 'ZH'], label='Language', value='EN')
            spd = gr.Slider(label='Speed', minimum=0.1, maximum=10.0, value=1.0, interactive=True, step=0.1)
            text = gr.Textbox(label="Text to speak", value=default_text_dict['EN'])
            language.input(load_speakers, inputs=[language, text], outputs=[speaker, text])
        btn = gr.Button('Synthesize', variant='primary')
        aud = gr.Audio(interactive=False)
        btn.click(synthesize, inputs=[speaker, text, spd, language], outputs=[aud])
    return demo


def launch_ui(host: str = "0.0.0.0", port: int = 8888):
    demo = create_ui()
    demo.queue(api_open=False).launch(
        server_name=host, server_port=port,
        prevent_thread_lock=True,
    )


@click.command()
@click.option('--share', '-s', is_flag=True, default=False)
@click.option('--host', '-h', default="0.0.0.0")
@click.option('--port', '-p', type=int, default=8888)
@click.option('--device', '-d', default='auto')
def main(share, host, port, device):
    tts_engine.init_models(device)
    demo = create_ui()
    demo.queue(api_open=False).launch(
        share=share, server_name=host, server_port=port,
    )


if __name__ == "__main__":
    main()

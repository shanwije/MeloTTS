VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
SSL_CERT_FILE := $(shell $(PYTHON) -c "import certifi; print(certifi.where())" 2>/dev/null)

export SSL_CERT_FILE

.PHONY: install setup ui tts play clean

install:
	python3.12 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e .
	$(PIP) install soxr
	$(PYTHON) -m unidic download

setup: install
	$(PYTHON) melo/init_downloads.py

ui:
	$(PYTHON) melo/app.py --host 0.0.0.0 --port 8888

tts:
	@test -n "$(TEXT)" || (echo "Usage: make tts TEXT=\"Your text here\" [OUT=output.wav] [LANG=EN] [SPEAKER=EN-US] [SPEED=1.0]" && exit 1)
	$(PYTHON) -c "\
		from melo.api import TTS; \
		model = TTS(language='$(or $(LANG),EN)', device='cpu'); \
		ids = model.hps.data.spk2id; \
		model.tts_to_file('$(TEXT)', ids['$(or $(SPEAKER),EN-US)'], '$(or $(OUT),output.wav)', speed=$(or $(SPEED),1.0)); \
		print('Saved to $(or $(OUT),output.wav)')"

play: tts
	open $(or $(OUT),output.wav)

clean:
	rm -rf $(VENV) *.egg-info build dist

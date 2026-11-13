# Recovered example — source-only handoff

The scripts and data in this folder were recovered from a **prior 30-second still-image animation project**. Their source is preserved exactly as retrieved. Re-rendering from a clean clone **will not work** without the private aligned images, font, voice data and original editable archive.

Available here: render_cinematic.py, generate_speech.py, improve_audio.py, setup_audio_models.py, requirements.txt, timeline.json, dialogue TXT, subtitle SRT and ORIGINAL_README.md.

Expected but absent: assets/Garden_Base.png, assets/Garden_Ah_Blink.png, assets/Garden_Oh.png, assets/DejaVuSans-Bold.ttf and license, work/audio.wav, prior clips, original image frames and rendered MP4. The model installer downloads the free Kokoro model once; no paid API required.

With all approved original assets supplied:
~~~bash
cd examples/flower-friends
python -m pip install -r requirements.txt
python setup_audio_models.py
python generate_speech.py
python render_cinematic.py
~~~

Use this folder as a reference for speech-timed eyes/lips, not a working sample of transparent video extraction.

from flask import Flask, request, render_template
from azure_speech import text_to_speech_azure, evaluate_pronunciation
from audio_recording import record_audio
from ipa_conversion import convert_text_to_ipa

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    text = request.form['text']

    ipa_transcriptions = convert_text_to_ipa(text)
    elapsed_time = text_to_speech_azure(text)

    audio_data = record_audio(elapsed_time + 1)
    scores = evaluate_pronunciation(audio_data, text)

    if scores:
        return render_template('result.html', scores=scores, ipa_transcriptions=ipa_transcriptions)
    else:
        return "Speech could not be recognized.", 500

if __name__ == '__main__':
    app.run(debug=True)

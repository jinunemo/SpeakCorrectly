import os
import time
import azure.cognitiveservices.speech as speechsdk
from io import BytesIO

class WavStreamReader(speechsdk.audio.PullAudioInputStreamCallback):
    def __init__(self, audio_data):
        super().__init__()
        self.audio_data = audio_data

    def read(self, buffer: memoryview) -> int:
        size = buffer.nbytes
        data = self.audio_data.read(size)
        buffer[:len(data)] = data
        return len(data)

    def close(self):
        self.audio_data.close()

def text_to_speech_azure(text):
    subscription_key = os.getenv("AZURE_SPEECH_KEY")
    service_region = os.getenv("AZURE_SPEECH_REGION")

    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=service_region)
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    start_time = time.time()
    result = synthesizer.speak_text_async(text).get()
    end_time = time.time()

    elapsed_time = end_time - start_time

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return elapsed_time
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        raise Exception(f"Speech synthesis canceled: {cancellation_details.reason}")
    return None

def evaluate_pronunciation(audio_data, reference_text):
    subscription_key = os.getenv("AZURE_SPEECH_KEY")
    service_region = os.getenv("AZURE_SPEECH_REGION")

    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=service_region)
    audio_input = speechsdk.audio.AudioConfig(stream=speechsdk.audio.PullAudioInputStream(WavStreamReader(audio_data)))

    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=reference_text,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
        enable_miscue=True
    )

    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)
    pronunciation_config.apply_to(recognizer)

    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        pronunciation_result = speechsdk.PronunciationAssessmentResult(result)
        scores = []
        for word_info in pronunciation_result.words:
            scores.append({
                "word": word_info.word,
                "accuracy": word_info.accuracy_score,
                "phonemes": [{"phoneme": p.phoneme, "accuracy": p.accuracy_score} for p in word_info.phonemes]
            })
        return scores
    else:
        return None

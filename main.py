import os
import time
import azure.cognitiveservices.speech as speechsdk
import pyaudio
import wave
import io
import numpy as np
import pygame
import eng_to_ipa as ipa

# Azure Speech 서비스 정보 설정
subscription_key = os.getenv("AZURE_SPEECH_KEY")
service_region = os.getenv("AZURE_SPEECH_REGION")

class WavStreamReader(speechsdk.audio.PullAudioInputStreamCallback):
    """BytesIO에서 읽은 데이터를 Azure의 PullAudioInputStreamCallback에 연결"""
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
    """Azure TTS를 사용하여 텍스트를 음성으로 변환 및 재생, 재생 시간 반환"""
    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=service_region)
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    start_time = time.time()  # 시작 시간 기록
    result = synthesizer.speak_text_async(text).get()
    end_time = time.time()  # 종료 시간 기록

    elapsed_time = end_time - start_time  # 재생 시간 계산

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Speech synthesized for text: [{text}] in {elapsed_time:.2f} seconds.")
        return elapsed_time
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
        return None

def determine_speech_speed(elapsed_time, word_count):
    """TTS 재생 시간과 단어 수를 기반으로 말하기 속도를 결정"""
    words_per_minute = (word_count / elapsed_time) * 60
    if words_per_minute < 100:
        return 'slow'
    elif words_per_minute <= 160:
        return 'normal'
    else:
        return 'fast'

def estimate_recording_time(text, speech_speed):
    """텍스트 길이에 따라 녹음 시간을 추정"""
    if speech_speed == 'slow':
        words_per_minute = 100
    elif speech_speed == 'normal':
        words_per_minute = 130
    elif speech_speed == 'fast':
        words_per_minute = 160
    else:
        raise ValueError("speech_speed must be 'slow', 'normal', or 'fast'")

    word_count = len(text.split())
    estimated_time = (word_count / words_per_minute) * 60
    return estimated_time

def play_beep_sound(sound_file):
    """beep.mp3 파일을 pygame을 이용해 재생"""
    pygame.mixer.init()
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        continue

def record_audio(record_seconds, volume_boost=1.0):
    """마이크로부터 음성을 녹음하여 메모리 내의 WAV 데이터로 반환하고 볼륨을 조정"""
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    play_beep_sound("beep.mp3")  # 녹음 시작 전 beep.mp3 재생

    time.sleep(1)  # 녹음 시작 전에 1초 마진 추가

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Recording...")
    frames = []

    for _ in range(0, int(RATE / CHUNK * record_seconds)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # WAV 데이터 메모리에 저장
    audio_buffer = io.BytesIO()
    wf = wave.open(audio_buffer, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)

    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
    audio_data = np.int16(audio_data * volume_boost)  # 볼륨 증가
    wf.writeframes(audio_data.tobytes())

    wf.close()
    audio_buffer.seek(0)
    return audio_buffer

def evaluate_pronunciation(audio_data, reference_text):
    """녹음된 음성을 Azure Speech 서비스에 보내어 발음 평가 수행"""
    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=service_region)
    audio_input = speechsdk.audio.AudioConfig(stream=speechsdk.audio.PullAudioInputStream(WavStreamReader(audio_data)))

    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=reference_text,  # 사용자가 입력한 참조 텍스트
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
        enable_miscue=True
    )

    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)
    pronunciation_config.apply_to(recognizer)

    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        pronunciation_result = speechsdk.PronunciationAssessmentResult(result)
        print(f"Recognized: {result.text}")
        print(f"Pronunciation Accuracy Score: {pronunciation_result.accuracy_score:.2f}")
        print(f"Pronunciation Fluency Score: {pronunciation_result.fluency_score:.2f}")
        print(f"Pronunciation Completeness Score: {pronunciation_result.completeness_score:.2f}")

        phoneme_scores = pronunciation_result.words
        for word_info in phoneme_scores:
            word = word_info.word
            ipa_transcription = ipa.convert(word)
            print(f"Word: {word}, IPA: {ipa_transcription}, Accuracy: {word_info.accuracy_score:.2f}")
            for phoneme_info in word_info.phonemes:
                print(f"  Phoneme: {phoneme_info.phoneme}, Accuracy: {phoneme_info.accuracy_score:.2f}")
    else:
        print("Speech could not be recognized.")

# 사용자 입력 받기
reference_text = input("Please enter the sentence you want to practice: ")

# 입력된 문장의 단어별 IPA 발음 기호 표기
print("IPA transcription for each word:")
for word in reference_text.split():
    ipa_transcription = ipa.convert(word)
    print(f"Word: {word}, IPA: {ipa_transcription}")

# 입력된 문장을 Azure TTS로 읽어주고 걸린 시간 측정
elapsed_time = text_to_speech_azure(reference_text)

# 입력된 문장의 단어 수 계산
word_count = len(reference_text.split())

# 말하기 속도 결정
speech_speed = determine_speech_speed(elapsed_time, word_count)
print(f"Determined speech speed: {speech_speed}")

# 입력된 문장에 따라 녹음 시간 추정
record_seconds = estimate_recording_time(reference_text, speech_speed)

# 녹음 및 평가 실행
audio_data = record_audio(record_seconds=record_seconds)
evaluate_pronunciation(audio_data, reference_text)

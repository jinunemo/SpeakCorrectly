import pyaudio
import wave
import io
import numpy as np  # numpy가 필요합니다.
import time
from beep_sound import play_beep_sound 

def record_audio(record_seconds, volume_boost=1.0):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    play_beep_sound("beep.mp3")

    # 1초 대기 후 녹음 시작
    time.sleep(1)

    frames = []

    for _ in range(0, int(RATE / CHUNK * record_seconds)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    audio_buffer = io.BytesIO()
    wf = wave.open(audio_buffer, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)

    audio_data = b''.join(frames)
    audio_data = np.frombuffer(audio_data, dtype=np.int16)
    audio_data = np.int16(audio_data * volume_boost)
    wf.writeframes(audio_data.tobytes())

    wf.close()
    audio_buffer.seek(0)
    return audio_buffer

import unittest
from azure_speech import text_to_speech_azure, evaluate_pronunciation
from io import BytesIO

class TestAzureSpeech(unittest.TestCase):
    def test_text_to_speech_azure(self):
        elapsed_time = text_to_speech_azure("Hello world")
        self.assertIsNotNone(elapsed_time)
        self.assertGreater(elapsed_time, 0)

    def test_evaluate_pronunciation(self):
        dummy_audio = BytesIO()  # 빈 BytesIO 객체
        result = evaluate_pronunciation(dummy_audio, "Hello world")
        self.assertIsNone(result)  # 실제 음성이 없으므로 None이 반환됨

if __name__ == '__main__':
    unittest.main()

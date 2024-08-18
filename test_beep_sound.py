import unittest
from beep_sound import play_beep_sound

class TestBeepSound(unittest.TestCase):
    def test_play_beep_sound(self):
        # 테스트는 간단히 호출로 진행하지만 실제 음성 재생 테스트는 환경 의존적일 수 있음
        try:
            play_beep_sound("beep.mp3")
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"play_beep_sound raised an exception: {str(e)}")

if __name__ == '__main__':
    unittest.main()

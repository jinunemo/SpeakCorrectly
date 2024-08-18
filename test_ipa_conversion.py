import unittest
from ipa_conversion import convert_text_to_ipa

class TestIPAConversion(unittest.TestCase):
    def test_convert_text_to_ipa(self):
        ipa_transcriptions = convert_text_to_ipa("Hello world")
        self.assertIn("Hello", ipa_transcriptions)
        self.assertIn("world", ipa_transcriptions)

if __name__ == '__main__':
    unittest.main()

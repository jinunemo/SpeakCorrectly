import eng_to_ipa as ipa

def convert_text_to_ipa(text):
    ipa_transcriptions = {}
    words = text.split()
    for word in words:
        ipa_transcriptions[word] = ipa.convert(word)
    return ipa_transcriptions

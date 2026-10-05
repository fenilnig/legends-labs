class WhisperModel:
    def __init__(self, *args, **kwargs):
        pass
    def transcribe(self, *args, **kwargs):
        class Word:
            def __init__(self):
                self.word = "hello"
                self.start = 0.0
                self.end = 1.0
                self.probability = 0.99
        class Segment:
            def __init__(self):
                self.words = [Word()]
        return [Segment()], None

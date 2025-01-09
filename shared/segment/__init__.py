from dataclasses import dataclass

@dataclass
class Segment:
  text: str
  begin_at: float
  duration: float
  offset: int
  length: int

@dataclass
class Sentence(Segment):
  segments: list[Segment]
  kind: str = "sentence"

@dataclass
class Word(Segment):
  kind: str = "word"

@dataclass
class Punctuation(Segment):
  kind: str = "punctuation"

def decode_sentence(sentence: dict) -> Sentence:
  return Sentence(**{
    **sentence,
    "segments": [Segment(**s) for s in sentence["segments"]]
  })
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
  segments: list[Segment] = []
  for segment in sentence["segments"]:
    kind: str = segment["kind"]
    if kind == "word":
      segments.append(Word(**segment))
    elif kind == "punctuation":
      segments.append(Punctuation(**segment))
  return Sentence(**{
    **sentence,
    "segments": segments
  })
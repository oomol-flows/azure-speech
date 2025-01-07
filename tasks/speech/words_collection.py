from io import StringIO
from sys import maxsize
from dataclasses import dataclass
from typing import cast, Any
from azure.cognitiveservices.speech import SpeechSynthesizer


@dataclass
class Segment:
  text: str = ""
  begin_at: float = 0.0
  duration: float = 0.0
  offset: int = 0
  length: int = 0

class Sentence(Segment):
  kind: str = "sentence"
  segments: list[Segment] = []

class Word(Segment):
  kind: str = "word"

class Punctuation(Segment):
  kind: str = "punctuation"

# https://learn.microsoft.com/zh-cn/azure/ai-services/speech-service/how-to-speech-synthesis?tabs=browserjs%2Cterminal&pivots=programming-language-python#customize-audio-format
class WordsCollection:
  def __init__(self, synthesizer: SpeechSynthesizer) -> None:
    synthesizer.synthesis_word_boundary.connect(self._on_word)
    self._sentences: list[Sentence] = []
    self._current_sentence: Sentence = Sentence()

  def take_sentences(self) -> list[Sentence]:
    self._handle_latest_setence()
    sentences = self._sentences
    self._sentences = []
    return sentences

  def _on_word(self, evt: Any):
    text: str = evt.text
    begin_at: float = evt.audio_offset / 10000.0
    duration: float = evt.duration.total_seconds() * 1000.0
    offset: int = evt.text_offset
    length: int = evt.word_length
    type = cast(str, evt.boundary_type).split(".")[-1]

    if type == "Word":
      self._current_sentence.segments.append(Word(
        text=text,
        begin_at=begin_at,
        duration=duration,
        offset=offset,
        length=length,
      ))
    elif type == "Punctuation":
      self._current_sentence.segments.append(Punctuation(
        text=text,
        begin_at=begin_at,
        duration=duration,
        offset=offset,
        length=length,
      ))
    elif type == "Sentence":
      self._current_sentence.text = text
      self._current_sentence.begin_at = begin_at
      self._current_sentence.duration = duration
      self._current_sentence.offset = offset
      self._current_sentence.length = length
      self._sentences.append(self._current_sentence)
      self._current_sentence = Sentence()

  def _handle_latest_setence(self):
    sentence = self._current_sentence
    if len(sentence.segments) == 0:
      return
    
    text_buffer = StringIO()
    begin_at: float = float("inf")
    end_at: float = 0.0
    text_begin: int = maxsize
    text_end: int = 0

    for segment in sentence.segments:
      text_buffer.write(segment.text)
      begin_at = min(begin_at, segment.begin_at)
      end_at = max(end_at, segment.begin_at + segment.duration)
      text_begin = min(text_begin, segment.offset)
      text_end = max(text_end, segment.offset + segment.length)
    
    sentence.text = text_buffer.getvalue()
    sentence.begin_at = begin_at
    sentence.duration = end_at - begin_at
    sentence.offset = text_begin
    sentence.length = text_end - text_begin

    self._sentences.append(sentence)
    self._current_sentence = Sentence()
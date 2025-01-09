from io import StringIO
from sys import maxsize
from typing import Any

from azure.cognitiveservices.speech import SpeechSynthesizer, SpeechSynthesisBoundaryType
from shared.segment import Punctuation, Segment, Sentence, Word

# https://learn.microsoft.com/zh-cn/azure/ai-services/speech-service/how-to-speech-synthesis?tabs=browserjs%2Cterminal&pivots=programming-language-python#customize-audio-format
class WordsCollection:
  def __init__(
      self, 
      synthesizer: SpeechSynthesizer,
      only_sentence: bool,
    ) -> None:
    synthesizer.synthesis_word_boundary.connect(self._on_word)
    self._only_sentence: bool = only_sentence
    self._segments: list[Segment] = []
    self._sentences: list[Sentence] = []

  def take_sentences(self) -> list[Sentence]:
    for segment in self._segments:
      sentence = self._find_sentence(segment.offset)
      if sentence is not None:
        sentence.segments.append(segment)
    for sentence in self._sentences:
      sentence.segments = sorted(sentence.segments, key=lambda s: s.offset)
    return self._sentences

  def _find_sentence(self, offset: float) -> Sentence | None:
    for s in self._sentences:
      if s.offset <= offset < s.offset + s.length:
        return s
    return None

  def _on_word(self, evt: Any):
    text: str = evt.text
    begin_at: float = evt.audio_offset / 10000.0
    duration: float = evt.duration.total_seconds() * 1000.0
    offset: int = evt.text_offset
    length: int = evt.word_length
    type: SpeechSynthesisBoundaryType = evt.boundary_type

    if type == SpeechSynthesisBoundaryType.Word and not self._only_sentence:
      self._segments.append(Word(
        text=text,
        begin_at=begin_at,
        duration=duration,
        offset=offset,
        length=length,
      ))
    elif type == SpeechSynthesisBoundaryType.Punctuation and not self._only_sentence:
      self._segments.append(Punctuation(
        text=text,
        begin_at=begin_at,
        duration=duration,
        offset=offset,
        length=length,
      ))
    elif type == SpeechSynthesisBoundaryType.Sentence:
      self._sentences.append(Sentence(
        text=text,
        begin_at=begin_at,
        duration=duration,
        offset=offset,
        length=length,
        segments=[],
      ))
from math import floor
from io import StringIO
from shared.segment import decode_sentence


def main(params: dict):
  buffer = StringIO()
  sentences: list[dict] = params["sentences"]

  for i, json_sentence in enumerate(sentences):
    sentence = decode_sentence(json_sentence)
    buffer.write(str(i + 1))
    buffer.write("\n")
    buffer.write(_format_time(sentence.begin_at))
    buffer.write(" --> ")
    buffer.write(_format_time(sentence.begin_at + sentence.duration))
    buffer.write("\n")
    buffer.write(sentence.text)
    if i < len(sentences) - 1:
      buffer.write("\n\n")

  return { "srt": buffer.getvalue() }

def _format_time(milliseconds: float):
  milliseconds = floor(milliseconds)
  seconds = milliseconds // 1000
  minutes = seconds // 60
  hours = minutes // 60
  return f"{hours:02}:{minutes % 60:02}:{seconds % 60:02},{milliseconds % 1000:03}"
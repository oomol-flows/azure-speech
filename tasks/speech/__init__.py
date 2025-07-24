import os

from dataclasses import asdict
from typing import cast, Literal, Any
from oocana import Context
from azure.cognitiveservices.speech import SpeechSynthesizer, SpeechSynthesisResult, ResultReason, SpeechConfig, PropertyId, CancellationReason
from azure.cognitiveservices.speech.audio import AudioOutputConfig
from .words_collection import WordsCollection


# https://learn.microsoft.com/zh-cn/azure/ai-services/speech-service/get-started-text-to-speech?tabs=linux%2Cterminal&pivots=programming-language-python
# https://learn.microsoft.com/zh-cn/azure/ai-services/speech-service/language-support?tabs=tts
def main(params: dict, context: Context):
  output_path: str | None = params["output_path"]
  if output_path is None:
    output_path = os.path.join(
      context.session_dir,
      "azure-speech",
      f"{context.job_id}.wav",
    )
  speech_config = SpeechConfig(
    subscription=params["key"],
    region=params["region"],
  )
  speech_config.set_property(
    property_id=PropertyId.SpeechServiceResponse_RequestSentenceBoundary,
    value="true",
  )
  audio_config = AudioOutputConfig(
    use_default_speaker=True,
    stream=cast(Any, None),
    filename=output_path,
  )
  text: str = params["text"]
  granlarity: Literal["none", "sentence", "word"] = params["granularity"]

  if granlarity != "none":
    speech_config.request_word_level_timestamps()

  speech_config.speech_synthesis_voice_name=params["voice"]
  speech_synthesizer = SpeechSynthesizer(
    speech_config=speech_config,
    audio_config=audio_config,
  )
  words: WordsCollection | None = None

  if granlarity != "none":
    words = WordsCollection(
      synthesizer=speech_synthesizer,
      only_sentence=(granlarity == "sentence"),
    )
  result = speech_synthesizer.speak_text_async(text).get()
  result = cast(SpeechSynthesisResult, result)

  _raise_if_find_error(result)

  return {
    "output_path": output_path,
    "sentences": _serialize_sentences(words),
  }

def _raise_if_find_error(result: SpeechSynthesisResult):
  if result.reason == ResultReason.Canceled:
    details = result.cancellation_details
    print("Speech synthesis canceled: {}".format(details.reason))
    if details.reason == CancellationReason.Error:
      if details.error_details:
        print("Error details: {}".format(details.error_details))
        print("Did you set the speech resource key and region values?")
    raise Exception("Speech synthesis failed.")

def _serialize_sentences(words: WordsCollection | None) -> list[dict]:
  if words is None:
    return []
  else:
    return [asdict(s) for s in words.take_sentences()]
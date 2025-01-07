import threading
import azure.cognitiveservices.speech as speechsdk

from typing import cast, Any

# https://learn.microsoft.com/zh-cn/azure/ai-services/speech-service/get-started-text-to-speech?tabs=linux%2Cterminal&pivots=programming-language-python
# https://learn.microsoft.com/zh-cn/azure/ai-services/speech-service/language-support?tabs=tts
def main(params: dict):
  # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
  speech_config = speechsdk.SpeechConfig(
    subscription=params["SPEECH_KEY"], 
    region=params["SPEECH_REGION"],
  )
  speech_config.set_property(
    property_id=speechsdk.PropertyId.SpeechServiceResponse_RequestSentenceBoundary, value='true',
  )
  speech_config.request_word_level_timestamps()
  audio_config = speechsdk.audio.AudioOutputConfig(
    use_default_speaker=True,
    stream=cast(Any, None),
    filename=params["output_path"],
  )
  # The neural multilingual voice can speak different languages based on the input text.
  speech_config.speech_synthesis_voice_name=params["voice"]
  speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
  text = params["speek_text"]

  words: list = []
  words_lock = threading.Lock()

  def word_boundary_handler(evt):
    nonlocal words, words_lock
    with words_lock:
      words.append(f'Word: {evt.text}, Start: {evt.audio_offset / 10000} ms, Duration: {evt.duration.total_seconds()*1000}, Start(length): {evt.text_offset}, Duration(length): {evt.word_length}, Type: {str(evt.boundary_type).split(".")[-1]} \n')

  speech_synthesizer.synthesis_word_boundary.connect(word_boundary_handler)
  speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
  speech_synthesis_result = cast(speechsdk.SpeechSynthesisResult, speech_synthesis_result)

  if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Speech synthesized for text [{}]".format(text))
  elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = speech_synthesis_result.cancellation_details
    print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
      if cancellation_details.error_details:
        print("Error details: {}".format(cancellation_details.error_details))
        print("Did you set the speech resource key and region values?")
    raise Exception("Speech synthesis failed.")

  # TODO: https://learn.microsoft.com/zh-cn/azure/ai-services/speech-service/how-to-speech-synthesis?tabs=browserjs%2Cterminal&pivots=programming-language-python#customize-audio-format
  with words_lock:
    for word in words:
      print(word)
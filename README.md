# azure-speech

Use Azure AI Speech to synthesize the input text into a human-like voice to read the text and finally output an audio file.

## Speech

Synthesize the text in `text` into human voice and output it as an audio file in `output_path`. At the same time, output the relevant information (timestamp) of matching text and human voice in the `sentences` field.

`voice` represents the virtual actor of synthesized human voice, please refer to the [document](https://learn.microsoft.com/zh-cn/azure/ai-services/speech-service/language-support?tabs=tts) for details.

The `granularity` field represents the granularity of the timestamp in the `sentences` field. It can be accurate to word.

## Sentences to SRT

Convert the contents of `sentences` in the Speech block to text in an SRT file.
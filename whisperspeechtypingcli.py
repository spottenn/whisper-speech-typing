import argparse
from recorder import Recorder
from localtranscriber import LocalTranscriber
from texttyper import TextTyper
from hotkeyhandler import HotkeyHandler

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='Voice typing script.')
        parser.add_argument('--model_size', type=str, default='medium', help='Size of the Whisper model')
        parser.add_argument('--device', type=str, default='cuda', help='Device to run the Whisper model on')
        parser.add_argument('--compute_type', type=str, default='float16', help='Compute datatype for the Whisper model')
        parser.add_argument('--language', type=str, default='en', help='Language for the Whisper model')
        parser.add_argument('--hotkey', type=str, default='f4', help='Hotkey to start/stop audio capture')
        parser.add_argument('--type_hotkey', type=str, default='f2', help='Hotkey to just type the transcription')
        parser.add_argument('--no-buffer', action='store_false', dest='buffer', default=True,
                            help='Do not buffer one second of audio before hotkey is pressed. May reduce power usage at the expense of potentially losing audio at the beginning.')
        args = parser.parse_args()

        recorder = Recorder(buffer=args.buffer)
        transcriber = LocalTranscriber(model_size=args.model_size, compute_type=args.compute_type, language=args.language, device=args.device)
        text_typer = TextTyper()
        hotkey_handler = HotkeyHandler(hotkey=args.hotkey, retype_hotkey=args.type_hotkey, recorder=recorder, transcriber=transcriber, texttyper=text_typer)

        hotkey_handler.main()
    except Exception as e:
        print(e)

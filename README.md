# Whisper Speech Typing: Speech-to-Text Typing with Faster Whisper
___
## Project Status

Current progress:
- ✅ Core functionality for speech capture and transcription.
- ✅ Integration with Faster Whisper API.
- ✅ System tray and floating window GUIs.
- ✅ UI for adjusting settings, model, and hotkeys.
- ⬜️ Cross-platform compatibility (Linux and macOS).
- ⬜️ Error handling and recovery.
- ⬜️ Debug logging.
- ⬜️ Multi-language support (English only for now).

Updates will be provided as development progresses.

## Potential Enhancements:

- **Server Backend:** Process audio models remotely. (WhisperLive?)
- **Live Transcription:** Real-time transcription with live text preview. (WhisperLive?)

___
## Quick Start
1. Make sure you have Python, and the 2 NVIDIA libraries from the [requirements](#requirements-and-pre-installation) section. 
2. Open a terminal as an administrator and run these commands
```commandline
git clone https://github.com/spottenn/whisper-speech-typing.git
cd whisper-speech-typing
pip install -r requirements.txt
python whisperspeechtyping.py
```
3. Wait for the program to download the model and initialize. When it is ready a green microphone will be displayed
4. Place cursor where you want to type, hold F4 and speak, then let go to type.

## Overview
This project provides a Python program for real-time speech-to-text typing using the Faster Whisper API. The application captures audio from the default microphone, transcribes it on-the-fly, and outputs the transcribed text to the current location of the cursor.

## Accuracy, Punctuation, Capitalization, and Multilingual
Since this uses the Whisper models, the speech-to-text typing is among the most accurate ever and includes __automatic punctuation and capitalization!__ The large-v2 model is even __multilingual!__  

For details on these, see the [papers](https://cdn.openai.com/papers/whisper.pdf) and benchmarks on the OpenAI Whisper models. 


## Performance and Accuracy
In general the larger models are slower, but more accurate while the smaller ones are the opposite. 

The model works in segments, which are audio clips of 20-30 seconds. The segment transcription times are fairly static between runs on the same hardware, with the exception that the first segment of a recording takes ~%60-80 longer than the others. In practice, this means that if you are speaking longer phrases and sentences, the typing feels faster than if you speak just a few words at a time.

This software should work on most desktop Operating Systems with a CUDA compatible GPU, although it has been primarily tested on Windows 10 and Windows 11. A GPU is required for real-time voice typing performance. Performance estimates are as follows:
- On an RTX 2070 Super, with the `large-v2` model, the wait is approximately 2 seconds for the first segment.
- On a Quadro P1000 Mobile, with the `medium` size model, float32 mode*, the wait is approximately 3-5 seconds for the first segment.

*Since this project uses the faster-whisper models, which are float16, float32 is generally not recommended since the speed will decrease and memory usage will increase with no boost to accuracy. The exception is if your card does not support hardware float16.
### Note on VRAM
The performance greatly worsens or the program may not even run if the graphics card does not have enough room to store the model entirely in its VRAM. In practice this means ~3.7 GB for Large-v2 if float16 operations are supported, and double that if not. That is why I had to run the medium model on the P1000. 

## Requirements and Pre-Installation
- Python 3.8 or greater

GPU execution requires the following NVIDIA libraries to be installed:
- cuBLAS for CUDA 11
- cuDNN 8 for CUDA 11

There are multiple ways to install these libraries. Please refer to the [Faster Whisper Requirements Section](https://github.com/guillaumekln/faster-whisper#requirements) for detailed instructions and options. 

Windows only: I used Purfview's zip file that has the required NVIDIA libraries for Windows in a [single archive](https://github.com/Purfview/whisper-standalone-win/releases/tag/libs) from [whisper-standalone-win](https://github.com/Purfview/whisper-standalone-win). Decompress the archive and place the libraries in a the same directory as the script.

## Usage

### General Instructions
1. Ensure you are running the script as an administrator.
2. Once the script is running, press and hold the specified hotkey (default is F4) to start capturing audio.
3. Release the hotkey to stop capturing and start the transcription process.
4. The transcribed text will be typed out at the current location of the cursor.

### Command Line Arguments
- `--model_size`: Size of the Whisper model (default: 'large-v2')
- `--device`: Device to run the Whisper model on (default: 'cuda')
- `--compute_type`: Compute type for the Whisper model (default: 'float16')
- `--hotkey`: Hotkey to start/stop audio capture (default: 'f4')

## Credits
Special thanks to the Faster Whisper project for providing the speech-to-text API utilized in this application. The project can be found [here](https://github.com/guillaumekln/faster-whisper).
Also, special thanks to openAI for open-sourcing their whisper models and making high quality STT with automatic capitalization and punctuation available.

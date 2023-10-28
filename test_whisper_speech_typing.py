# CURRENTLY NON-FUNCTIONAL!!!!
import io
import pytest
from unittest.mock import patch, Mock, MagicMock
from whisper_speech_typing import RealTimeTranscriber

# Mocking the dependencies
pyaudio_mock = Mock()
numpy_mock = Mock()
keyboard_mock = Mock()
pyautogui_mock = Mock()
faster_whisper_mock = Mock()
threading_mock = Mock()
time_mock = Mock()

@pytest.fixture
def transcriber():
    with patch('pyaudio.PyAudio', return_value=pyaudio_mock), \
         patch('numpy.frombuffer', return_value=numpy_mock), \
         patch('keyboard.is_pressed', return_value=keyboard_mock), \
         patch('pyautogui.write', return_value=pyautogui_mock), \
         patch('faster_whisper.WhisperModel', return_value=faster_whisper_mock), \
         patch('threading.Thread', return_value=threading_mock), \
         patch('time.sleep', return_value=time_mock):
        transcriber = RealTimeTranscriber('base', 'cpu', 'float32', "", 'f4', 'f2', False)
        yield transcriber

def test_audio_callback(transcriber):
    in_data = b'\x01\x02\x03\x04'
    frame_count = 4
    time_info = None
    status = None
    result = transcriber.audio_callback(in_data, frame_count, time_info, status)
    assert result == (None, pyaudio_mock.paContinue)
    assert len(transcriber.frames) == 0

def test_start_audio_capture(transcriber):
    transcriber.start_audio_capture()
    assert transcriber.is_recording is True
    assert len(transcriber.frames) == 0

def test_stop_audio_capture(transcriber):
    transcriber.frames.append(b'\x01\x02\x03\x04')
    audio = transcriber.stop_audio_capture()
    assert transcriber.is_recording is False
    assert isinstance(audio, io.BytesIO)

def test_transcribe_audio(transcriber):
    audio = io.BytesIO(b'\x01\x02\x03\x04')
    transcriber.model.transcribe.return_value = (['transcription'], None)
    result = transcriber.transcribe_audio(audio)
    assert result == 'transcription'

def test_type_text(transcriber):
    text = 'test text'
    transcriber.type_text(text)
    pyautogui_mock.write.assert_called_with(text)

def test_main(transcriber):
    keyboard_mock.is_pressed.side_effect = [True, False, False]
    with pytest.raises(StopIteration):
        transcriber.main()
    assert keyboard_mock.is_pressed.call_count == 3
    assert pyautogui_mock.write.call_count == 1


def test_process_hotkeys_capture_audio(transcriber):
    with patch('keyboard.is_pressed', side_effect=[True, False]) as keyboard_mock, \
            patch('time.sleep') as sleep_mock:
        transcriber.start_audio_capture = MagicMock()
        transcriber.stop_audio_capture = MagicMock(return_value=io.BytesIO(b'test'))
        transcriber.transcribe_audio = MagicMock(return_value='transcription')
        transcriber.type_text = MagicMock()

        result = transcriber.process_hotkeys()

        assert result is True
        keyboard_mock.assert_called_with(transcriber.hotkey)
        sleep_mock.assert_called_with(0.1)
        transcriber.start_audio_capture.assert_called_once()
        transcriber.stop_audio_capture.assert_called_once()
        transcriber.transcribe_audio.assert_called_once()
        transcriber.type_text.assert_called_once_with('transcription')


def test_process_hotkeys_retype_text(transcriber):
    with patch('keyboard.is_pressed', side_effect=[False, True]) as keyboard_mock, \
            patch('time.sleep') as sleep_mock:
        transcriber.transcription = 'previous transcription'
        transcriber.type_text = MagicMock()

        result = transcriber.process_hotkeys()

        assert result is True
        keyboard_mock.assert_any_call(transcriber.type_hotkey)
        sleep_mock.assert_called_with(0.2)
        transcriber.type_text.assert_called_once_with('previous transcription')

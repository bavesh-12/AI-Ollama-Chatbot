import speech_recognition as sr
import tempfile
import os
from pydub import AudioSegment
from fastapi import UploadFile

recognizer = sr.Recognizer()

def transcribe_audio_file(audio_file: UploadFile) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        content = audio_file.file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        if tmp_path.lower().endswith('.mp3'):
            try:
                audio = AudioSegment.from_mp3(tmp_path)
                wav_path = tmp_path.replace('.mp3', '.wav')
                audio.export(wav_path, format="wav")
                os.remove(tmp_path)
                tmp_path = wav_path
            except:
                pass
        
        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Speech recognition error: {e}"
    except Exception as e:
        return f"Error processing audio: {str(e)}"
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass

def transcribe_microphone(timeout: int = 5) -> str:
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.listen(source, timeout=timeout)
            text = recognizer.recognize_google(audio_data)
            return text
    except sr.WaitTimeoutError:
        return "No speech detected"
    except sr.UnknownValueError:
        return "Could not understand audio"
    except Exception as e:
        return f"Error: {str(e)}"
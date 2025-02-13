import os
import uuid
from faster_whisper import WhisperModel
from moviepy.editor import VideoFileClip
from pydub import AudioSegment

CHUNK_LENGTH_MS = 600000  # 10 minutes in milliseconds
UPLOADS_DIR = 'uploads'

def initialize_model(device="cpu", compute_type="int8"):
    """Initialize the Whisper model."""
    try:
        model = WhisperModel("large", device=device, compute_type=compute_type)
        return model
    except Exception as e:
        print(f"Error during initializing model: {e}")
        return None

def transcribe_audio(model, audio_path, beam_size=2):
    """Transcribe audio using the Whisper model."""
    try:
        segments, _ = model.transcribe(audio_path, beam_size=beam_size)
        return " ".join(segment.text for segment in segments)
    except Exception as e:
        print(f"Error during transcription of {audio_path}: {e}")
        return ""

def convert_video_to_wav(video_path, wav_path):
    """Extract audio from a video and save it as a WAV file."""
    try:
        with VideoFileClip(video_path) as video_clip:
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(wav_path, codec='pcm_s16le')
            audio_clip.close()
            video_clip.close()
    except Exception as e:
        print(f"Error during audio extraction: {e}")

def split_audio(audio_path, folder_path, chunk_length_ms=CHUNK_LENGTH_MS):
    """Split audio into smaller chunks and save them in the specified folder."""
    audio = AudioSegment.from_wav(audio_path)
    chunks = []
    
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i + chunk_length_ms]
        chunk_path = os.path.join(folder_path, f"chunk_{i // chunk_length_ms}.wav")
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    
    return chunks

def clean_up_files(file_paths):
    """Delete files from the filesystem."""
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
            
def generate_text(video_path, folder_path):
    """Process video: extract audio, split into chunks, and transcribe."""
    unique_id = str(uuid.uuid4())
    wav_path = os.path.join(folder_path, f'uploaded_audio_{unique_id}.wav')

    convert_video_to_wav(video_path, wav_path)
    chunk_paths = split_audio(wav_path, folder_path, chunk_length_ms=CHUNK_LENGTH_MS)

    model = initialize_model(device="cpu", compute_type="int8")

    full_transcription = []

    for chunk_path in chunk_paths:
        transcription_text = transcribe_audio(model, chunk_path, beam_size=2)
        full_transcription.append(transcription_text)

    clean_up_files([video_path, wav_path] + chunk_paths)

    return " ".join(full_transcription).strip()

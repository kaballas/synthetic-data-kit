from pathlib import Path
from typing import Union
import os
from openai import OpenAI

# Load .env from the repository root (c:\DTT\synthetic-data-kit\.env) if present.
repo_root = Path(__file__).parents[2]
dotenv_path = repo_root / ".env"
if dotenv_path.exists():
    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            # Do not overwrite existing environment variables
            os.environ.setdefault(k, v)

# Instantiate client after loading env
client = OpenAI()

def generate_speech_from_transcript(
    transcript_path: Union[str, Path],
    output_dir: Union[str, Path] | None = None,
    filename: str = "speech.mp3",
    voice: str = "coral",
    model: str = "gpt-4o-mini-tts",
    instructions: str = "Speak in a cheerful and positive tone.",
) -> Path:
    """
    Generate speech from a transcript file using the OpenAI TTS streaming API.
    Returns the path to the written audio file.
    """
    transcript_path = Path(transcript_path)
    if not transcript_path.exists():
        raise FileNotFoundError(f"Transcript not found: {transcript_path}")

    transcript_text = transcript_path.read_text(encoding="utf-8")

    if output_dir is None:
        output_dir = Path(__file__).parent / "audio"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    # Use the streaming TTS API and write the streamed response to a file.
    # Adjust the API call as needed if your OpenAI SDK version differs.
    try:
        with client.audio.speech.with_streaming_response.create(
            model=model,
            voice=voice,
            input=transcript_text,
            instructions=instructions,
        ) as response:
            response.stream_to_file(output_path)
    except Exception:
        raise

    return output_path

# Example usage (won't run on import)
if __name__ == "__main__":
    transcript = Path(r"c:\DTT\synthetic-data-kit\data\transcripts\Add New Employee To This Position_podcast_transcript.txt")
    out = generate_speech_from_transcript(transcript)
    print(f"Generated speech saved to: {out}")
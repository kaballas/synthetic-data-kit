# Podcast Generator Feature

## Overview

The Podcast Generator converts text documents into engaging conversational podcasts with two AI speakers. It can generate both transcripts and audio files using multiple Text-to-Speech (TTS) providers.

## Features

- **Two-Speaker Dialogue**: Person1 (main summarizer) and Person2 (questioner/clarifier)
- **Configurable Style**: Engaging, fast-paced, enthusiastic conversations
- **Multiple TTS Providers**: OpenAI, ElevenLabs, Edge (free), Gemini
- **Chunking Support**: Handles long documents by breaking them into discussion rounds
- **Engagement Techniques**: Rhetorical questions, anecdotes, analogies, and humor
- **Batch Processing**: Process entire directories at once
- **Auto-organization**: Moves processed files to `done/` subfolder

## Installation

### Required Dependencies

```bash
# Core dependencies (already included)
pip install -e .

# For audio generation (optional, based on TTS provider):

# OpenAI TTS
pip install openai pydub

# ElevenLabs TTS  
pip install elevenlabs pydub

# Edge TTS (Free, no API key needed)
pip install edge-tts pydub

# For audio processing (required if using any TTS)
pip install pydub

# FFmpeg (required for pydub audio processing)
# Windows: Download from https://ffmpeg.org/download.html
# macOS: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg
```

## Configuration

All podcast settings are in `synthetic_data_kit/config.yaml` under the `podcast:` section:

```yaml
podcast:
  # Conversation style
  conversation_style:
    - "engaging"
    - "fast-paced"
    - "enthusiastic"
  
  # Speaker roles
  roles:
    person1: "main summarizer"
    person2: "questioner/clarifier"
  
  # Branding
  podcast_name: "PODCASTIFY"
  podcast_tagline: "Your Personal Generative AI Podcast"
  
  # TTS providers
  text_to_speech:
    default_tts_model: "openai"  # or "elevenlabs", "edge", "gemini"
    
    openai:
      default_voices:
        question: "echo"
        answer: "shimmer"
      model: "tts-1-hd"
    
    edge:  # Free option
      default_voices:
        question: "en-US-JennyNeural"
        answer: "en-US-EricNeural"
```

## Usage

### Basic Usage (Transcript Only)

```bash
# Single file
synthetic-data-kit podcast document.txt

# Directory
synthetic-data-kit podcast ./data/parsed/
```

**Output:**
- `data/transcripts/document_podcast_transcript.txt` - Formatted transcript
- `data/generated/document_podcast_dialogue.json` - Dialogue JSON

### With Audio Generation

```bash
# Using OpenAI TTS (requires API key)
synthetic-data-kit podcast document.txt --audio --tts openai

# Using Edge TTS (free, no API key needed)
synthetic-data-kit podcast document.txt --audio --tts edge

# Using ElevenLabs TTS
synthetic-data-kit podcast document.txt --audio --tts elevenlabs
```

**Output:**
- Transcript and dialogue (as above)
- `data/audio/document_podcast.mp3` - Complete podcast audio

### Batch Processing

```bash
# Process entire directory
synthetic-data-kit podcast ./data/parsed/ --audio --tts edge -v

# Process with custom chunk size for long documents
synthetic-data-kit podcast ./data/parsed/ --num-chunks 6 -v
```

### Advanced Options

```bash
synthetic-data-kit podcast document.txt \
  --audio \
  --tts openai \
  --model gpt-5-mini \
  --output-dir ./my-podcasts \
  --num-chunks 8 \
  --verbose
```

## Command Options

```
Arguments:
  input                Input file or directory

Options:
  --output-dir, -o     Output directory for podcast files
  --audio, -a          Generate audio file (requires TTS setup)
  --tts                TTS provider: openai|elevenlabs|edge|gemini
  --model, -m          LLM model for dialogue generation
  --num-chunks         Number of dialogue chunks for long content
  --verbose, -v        Show detailed output
  --preview            Preview files without processing
  --api-base           Custom API base URL
  --help               Show help message
```

## TTS Provider Setup

### OpenAI TTS

**Requirements:**
- OpenAI API key or compatible API endpoint
- `pip install openai pydub`

**Setup:**
```bash
# Set API key
export OPENAI_API_KEY="your-key-here"
# or
export API_ENDPOINT_KEY="your-key-here"

# Configure in config.yaml (optional)
podcast:
  text_to_speech:
    default_tts_model: "openai"
    openai:
      model: "tts-1-hd"  # or "tts-1" for faster generation
      default_voices:
        question: "echo"  # Voices: alloy, echo, fable, onyx, nova, shimmer
        answer: "shimmer"
```

### Edge TTS (FREE)

**Requirements:**
- No API key needed!
- `pip install edge-tts pydub`

**Setup:**
```bash
# That's it! Just install and use
synthetic-data-kit podcast document.txt --audio --tts edge
```

**Available Voices:**
- `en-US-JennyNeural` (Female)
- `en-US-EricNeural` (Male)
- `en-US-GuyNeural` (Male)
- `en-US-AriaNeural` (Female)
- And many more languages/voices

### ElevenLabs TTS

**Requirements:**
- ElevenLabs API key
- `pip install elevenlabs pydub`

**Setup:**
```bash
# Set API key
export ELEVENLABS_API_KEY="your-key-here"

# Configure voices in config.yaml
podcast:
  text_to_speech:
    default_tts_model: "elevenlabs"
    elevenlabs:
      model: "eleven_multilingual_v2"
      default_voices:
        question: "Chris"
        answer: "Jessica"
```

## Examples

### Example 1: Quick Podcast (No Audio)

```bash
synthetic-data-kit podcast report.txt
```

Creates transcript in minutes, perfect for reviewing content.

### Example 2: Full Podcast with Edge TTS (Free)

```bash
synthetic-data-kit podcast report.txt --audio --tts edge -v
```

Generates both transcript and audio using free Edge TTS.

### Example 3: Batch Process Directory

```bash
synthetic-data-kit podcast ./data/parsed/ --audio --tts edge -v
```

Converts all .txt files to podcasts, moves originals to `done/` folder.

### Example 4: Custom Configuration

```bash
# First, update config.yaml:
# podcast:
#   creativity: 1.5  # More creative dialogues
#   max_num_chunks: 10  # Longer podcasts

synthetic-data-kit podcast long-report.txt --audio --tts openai --num-chunks 10
```

## Output Structure

After running the podcast command:

```
data/
├── transcripts/
│   └── document_podcast_transcript.txt  # Human-readable transcript
├── generated/
│   └── document_podcast_dialogue.json   # Structured dialogue data
├── audio/
│   └── document_podcast.mp3             # Audio file (if --audio used)
└── parsed/
    ├── done/
    │   └── document.txt                 # Moved after processing
    └── other-file.txt                   # Not yet processed
```

## Transcript Format

```
=== PODCASTIFY ===
Your Personal Generative AI Podcast

==================================================

[00:00] Person1: Welcome to PODCASTIFY! Today we're diving into...

[00:15] Person2: That sounds fascinating! Can you break down what that means?

[00:25] Person1: Absolutely! Let me explain step by step...

...

[05:45] Person1: See You Next Time!
```

## Troubleshooting

### Issue: "OpenAI API key not found"

**Solution:**
```bash
export OPENAI_API_KEY="your-key-here"
# or
export API_ENDPOINT_KEY="your-key-here"
```

### Issue: "FFmpeg not found"

**Solution:**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html and add to PATH
```

### Issue: "Failed to generate dialogue"

**Solutions:**
- Check if LLM server is running (for local models)
- Verify API key is set (for cloud providers)
- Try with `--verbose` flag to see detailed errors
- Reduce `--num-chunks` for shorter content

### Issue: "Module 'pydub' not found"

**Solution:**
```bash
pip install pydub
# And ensure FFmpeg is installed (see above)
```

## Best Practices

1. **Start with Edge TTS**: It's free and works well for testing
2. **Use verbose mode**: Always use `-v` when processing multiple files
3. **Chunk appropriately**: For long documents (>10K words), use `--num-chunks 6-8`
4. **Preview first**: Use `--preview` on directories to see what will be processed
5. **Test on single files**: Before batch processing, test on one file

## Integration with Other Commands

The podcast generator works seamlessly with other SDK commands:

```bash
# Full pipeline example:
# 1. Ingest PDFs
synthetic-data-kit ingest ./reports/ -v

# 2. Generate podcasts from parsed text
synthetic-data-kit podcast ./data/parsed/ --audio --tts edge -v

# 3. Files automatically move to done/ folders
```

## API Reference

### PodcastGenerator Class

```python
from synthetic_data_kit.generators.podcast_generator import PodcastGenerator
from synthetic_data_kit.models.llm_client import LLMClient

# Initialize
client = LLMClient(provider="api-endpoint")
generator = PodcastGenerator(client)

# Generate dialogue
dialogue = generator.generate_podcast_dialogue(
    text="Your document text here",
    num_chunks=5,
    verbose=True
)

# Process complete document
result = generator.process_document(
    document_text="Your text",
    output_dir="./output",
    base_name="my_podcast",
    generate_audio=True,
    tts_provider="edge",
    verbose=True
)
```

## Customization

### Custom Podcast Name

Edit `config.yaml`:
```yaml
podcast:
  podcast_name: "My Custom Podcast"
  podcast_tagline: "Insights You Need"
```

### Custom Engagement Style

```yaml
podcast:
  conversation_style:
    - "professional"
    - "informative"
    - "concise"
  engagement_techniques:
    - "data points"
    - "case studies"
```

### Custom Voices

```yaml
podcast:
  text_to_speech:
    openai:
      default_voices:
        question: "fable"  # More storytelling voice
        answer: "nova"     # Clear, professional voice
```

## Performance Tips

- **Edge TTS**: Fastest and free, great for development
- **OpenAI TTS-1**: Faster than TTS-1-HD, good quality
- **Chunking**: Use smaller chunks (4-6) for faster generation
- **Parallel processing**: Process multiple files simultaneously

## Future Enhancements

Potential improvements:
- [ ] Multi-language support
- [ ] Background music integration
- [ ] Voice cloning for custom speakers
- [ ] Live streaming support
- [ ] Podcast RSS feed generation
- [ ] Chapter markers in audio
- [ ] Interactive transcripts

## Support

For issues or questions:
1. Check verbose output: `synthetic-data-kit podcast file.txt --audio --tts edge -v`
2. Review configuration: `synthetic_data_kit/config.yaml`
3. Check dependencies: `pip list | grep -E "(openai|elevenlabs|edge-tts|pydub)"`
4. Test with sample file first
5. Open an issue on GitHub with full error output

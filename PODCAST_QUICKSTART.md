# Quick Start: Podcast Generator

## 5-Minute Setup

### 1. Install Dependencies

```bash
# Basic (transcript only)
pip install -e .

# With Edge TTS (free audio generation)
pip install edge-tts pydub

# Install FFmpeg
# macOS: brew install ffmpeg
# Ubuntu: sudo apt-get install ffmpeg
# Windows: Download from https://ffmpeg.org
```

### 2. Test Basic Generation

```bash
# Create a test file
echo "Artificial Intelligence is transforming how we work and live. Machine learning algorithms can now process vast amounts of data and make predictions with remarkable accuracy. From healthcare to finance, AI applications are becoming increasingly sophisticated." > test.txt

# Generate podcast transcript only
synthetic-data-kit podcast test.txt -v

# ⚠️ Windows/PowerShell: Use quotes if path has spaces
synthetic-data-kit podcast "path with spaces/file name.txt" -v
```

**Output:**
```
✅ Podcast transcript saved to data/transcripts/test_podcast_transcript.txt
```

### 3. Generate with Audio (Free)

```bash
# Using free Edge TTS
synthetic-data-kit podcast test.txt --audio --tts edge -v
```

**Output:**
```
✅ Podcast transcript saved to data/transcripts/test_podcast_transcript.txt
🔊 Audio saved to data/audio/test_podcast.mp3
```

### 4. Process Multiple Files

```bash
# Put some .txt files in data/input/
# Then process them all
synthetic-data-kit podcast ./data/input/ --audio --tts edge -v
```

## What Just Happened?

1. **Dialogue Generation**: The LLM converted your text into a natural conversation between two speakers
2. **Transcript Creation**: A formatted transcript was saved with timestamps
3. **Audio Generation** (if using `--audio`): Each speaker's lines were converted to speech and combined
4. **Auto-Organization**: Original files were moved to `data/input/done/`

## Next Steps

### Use with Your Documents

```bash
# 1. Ingest your documents (PDF, DOCX, etc.)
synthetic-data-kit ingest my-document.pdf

# 2. Generate podcast from parsed text
synthetic-data-kit podcast ./data/parsed/ --audio --tts edge -v
```

### Try Different Voices

Edit `synthetic_data_kit/config.yaml`:

```yaml
podcast:
  text_to_speech:
    edge:
      default_voices:
        question: "en-US-GuyNeural"  # Change to male voice
        answer: "en-US-AriaNeural"   # Change to different female voice
```

### Use OpenAI TTS (Better Quality)

**Recommended: Use `.env` file**
```bash
# 1. Copy the template
cp .env.example .env

# 2. Edit .env and add your key:
OPENAI_API_KEY=sk-your-openai-key-here

# 3. Generate podcast
synthetic-data-kit podcast test.txt --audio --tts openai -v
```

**Alternative: Set environment variable directly**
```bash
# PowerShell
$env:OPENAI_API_KEY="sk-your-key"

# Linux/Mac
export OPENAI_API_KEY="sk-your-key"

# Generate with OpenAI (uses gpt-4o-mini-tts with coral and alloy voices)
synthetic-data-kit podcast test.txt --audio --tts openai -v
```

**📖 See [ENV_SETUP.md](ENV_SETUP.md) for complete environment variable guide.**

## Configuration Options

All settings in `synthetic_data_kit/config.yaml` under `podcast:` section.

**Quick customization:**

```yaml
podcast:
  podcast_name: "My Podcast"
  podcast_tagline: "Learning Made Easy"
  
  conversation_style:
    - "professional"  # Try: engaging, fast-paced, casual, professional
    - "informative"
  
  creativity: 1.5  # 0-2 scale (higher = more creative dialogue)
  
  max_num_chunks: 8  # For long documents
```

## Troubleshooting

**Problem:** "Got unexpected extra arguments"
- **Cause**: File path has spaces and isn't quoted
- **Solution**: Wrap the path in quotes: `synthetic-data-kit podcast "my file.txt"`

**Problem:** "FFmpeg not found"
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows: Download from https://ffmpeg.org and add to PATH
```

**Problem:** "Failed to generate dialogue"
- Check if your LLM server is running
- Verify API keys are set
- Try with `-v` flag for more details

**Problem:** "No module named 'pydub'"
```bash
pip install pydub
```

## Examples

### Example 1: News Article to Podcast

```bash
# Create article
cat > article.txt << EOF
Breaking: Scientists discover new treatment for common disease.
Researchers at the university have found a novel approach...
EOF

# Generate podcast
synthetic-data-kit podcast article.txt --audio --tts edge -v
```

### Example 2: Technical Documentation

```bash
# Your technical doc
synthetic-data-kit podcast ./docs/api-reference.txt --audio --tts edge -v
```

### Example 3: Batch Process Blog Posts

```bash
# All your blog posts
synthetic-data-kit podcast ./blog-posts/ --audio --tts edge -v
```

## Full Feature Guide

See [PODCAST_GENERATOR_GUIDE.md](PODCAST_GENERATOR_GUIDE.md) for:
- Complete TTS provider setup
- Advanced configuration options
- API reference
- Troubleshooting guide
- Best practices

## Summary

**Podcast Generator turns any text into conversational audio in 3 steps:**

1. `pip install edge-tts pydub` (one-time setup)
2. `synthetic-data-kit podcast yourfile.txt --audio --tts edge`
3. Listen to `data/audio/yourfile_podcast.mp3`

🎙️ **It's that simple!**

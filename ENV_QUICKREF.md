# 🚀 Environment Variables Quick Reference

## Setup in 3 Steps

```bash
# 1. Your .env file is already created!
# 2. Edit it with your keys
notepad .env  # Windows
nano .env     # Linux/Mac

# 3. Add your OpenAI key (for podcast TTS):
OPENAI_API_KEY=sk-your-actual-key-here
```

## Test It Works

```bash
# Test podcast generation with OpenAI TTS
synthetic-data-kit podcast "test.txt" --audio --tts openai -v
```

## Available Keys

| Variable | Purpose | Get Key From |
|----------|---------|--------------|
| `OPENAI_API_KEY` | OpenAI TTS (podcast audio) | [OpenAI Platform](https://platform.openai.com/api-keys) |
| `API_ENDPOINT_KEY` | LLM operations | Your LLM provider |
| `ELEVENLABS_API_KEY` | Premium TTS (optional) | [ElevenLabs](https://elevenlabs.io/) |
| `GOOGLE_API_KEY` | Gemini TTS (optional) | [Google AI Studio](https://makersuite.google.com/app/apikey) |

## Free Option (No Key Needed)

```bash
# Use Edge TTS - completely free!
synthetic-data-kit podcast "test.txt" --audio --tts edge -v
```

## File Format

```bash
# In .env file (NO quotes, NO spaces around =)
OPENAI_API_KEY=sk-proj-abc123xyz
API_ENDPOINT_KEY=your-key-here
```

## Troubleshooting

❌ **"API key not found"**
→ Check `.env` file exists in project root
→ Verify no quotes around values
→ Restart terminal

❌ **"Invalid API key"**
→ Verify key format (OpenAI starts with `sk-`)
→ Check for extra spaces or newlines
→ Regenerate key if needed

## Documentation

- **Full guide**: [ENV_SETUP.md](ENV_SETUP.md)
- **Podcast guide**: [PODCAST_QUICKSTART.md](PODCAST_QUICKSTART.md)
- **Voice guide**: [OPENAI_TTS_VOICES.md](OPENAI_TTS_VOICES.md)

---

💡 **Tip**: Use Edge TTS (`--tts edge`) for free testing, then switch to OpenAI TTS (`--tts openai`) for production!

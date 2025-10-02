# OpenAI TTS Voice Guide

## Overview

The podcast generator now uses the latest **`gpt-4o-mini-tts`** model from OpenAI, which supports:
- New high-quality voices (coral, alloy, echo, fable, onyx, nova, shimmer)
- Voice instructions for tone control
- Streaming response for efficient audio generation

## Available Voices

| Voice | Description | Best For |
|-------|-------------|----------|
| **coral** | Warm, friendly, engaging | Main narrator, explanations |
| **alloy** | Clear, balanced, neutral | Professional content, answers |
| **echo** | Confident, authoritative | Technical content, facts |
| **fable** | Expressive, storytelling | Narratives, questions |
| **onyx** | Deep, authoritative | Serious topics, analysis |
| **nova** | Energetic, youthful | Casual content, questions |
| **shimmer** | Soft, gentle | Calm explanations, meditation |

## Default Configuration

In `synthetic_data_kit/config.yaml`:

```yaml
podcast:
  text_to_speech:
    openai:
      default_voices:
        question: "coral"    # Person2 (the questioner)
        answer: "alloy"      # Person1 (main narrator)
      model: "gpt-4o-mini-tts"
      voice_instructions:
        question: "Speak in a curious and engaging tone, as if asking thoughtful questions."
        answer: "Speak in a clear, informative, and friendly tone, as if explaining concepts."
```

## Customizing Voices

### Example 1: Professional Podcast

```yaml
openai:
  default_voices:
    question: "echo"      # Confident questioner
    answer: "onyx"        # Authoritative explainer
  voice_instructions:
    question: "Speak with confidence and directness, asking probing questions."
    answer: "Speak authoritatively and precisely, like a subject matter expert."
```

### Example 2: Casual Learning Podcast

```yaml
openai:
  default_voices:
    question: "nova"      # Energetic, curious
    answer: "coral"       # Warm, friendly
  voice_instructions:
    question: "Speak with enthusiasm and curiosity, like an excited learner."
    answer: "Speak warmly and encouragingly, like a friendly teacher."
```

### Example 3: Storytelling Podcast

```yaml
openai:
  default_voices:
    question: "fable"     # Expressive questioner
    answer: "shimmer"     # Gentle narrator
  voice_instructions:
    question: "Speak expressively with emotional nuance, drawing listeners in."
    answer: "Speak gently and thoughtfully, like narrating a story."
```

## Voice Instructions Guide

Voice instructions control the **tone and delivery style**. Here are effective patterns:

### For Questions (Person2)
- **Curious**: "Speak with genuine curiosity, as if discovering something fascinating."
- **Challenging**: "Speak with polite skepticism, asking challenging follow-up questions."
- **Enthusiastic**: "Speak with excitement and energy, eager to learn more."
- **Analytical**: "Speak thoughtfully and precisely, asking for clarification and details."

### For Answers (Person1)
- **Educational**: "Speak clearly and patiently, like a teacher explaining to students."
- **Authoritative**: "Speak confidently and precisely, like an expert in the field."
- **Conversational**: "Speak naturally and warmly, like chatting with a friend."
- **Inspirational**: "Speak with passion and conviction, inspiring the listener."

## Usage Examples

### Generate with Default Settings

```powershell
synthetic-data-kit podcast "document.txt" --audio --tts openai -v
```

### Test Different Voices (Quick Edit)

1. Edit `synthetic_data_kit/config.yaml`
2. Change the `default_voices` section
3. Run the podcast command again

```powershell
synthetic-data-kit podcast "document.txt" --audio --tts openai -v
```

### Set API Key (PowerShell)

```powershell
# Set for current session
$env:OPENAI_API_KEY = "sk-your-api-key-here"

# Set permanently (Windows)
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-your-api-key-here', 'User')
```

### Set API Key (Linux/Mac)

```bash
# Set for current session
export OPENAI_API_KEY="sk-your-api-key-here"

# Set permanently (add to ~/.bashrc or ~/.zshrc)
echo 'export OPENAI_API_KEY="sk-your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

## Technical Details

### Streaming Response

The implementation uses `with_streaming_response.create()` for efficient audio generation:

```python
with client.audio.speech.with_streaming_response.create(
    model="gpt-4o-mini-tts",
    voice="coral",
    input=text,
    instructions="Speak in a cheerful and positive tone."
) as response:
    response.stream_to_file(output_path)
```

### Benefits
- ✅ Lower latency (starts receiving audio immediately)
- ✅ More efficient memory usage
- ✅ Better for long text inputs
- ✅ Supports tone control via instructions

## Cost Considerations

**OpenAI TTS Pricing** (as of 2025):
- `gpt-4o-mini-tts`: $0.015 per 1,000 characters
- Streaming has the same cost as non-streaming

**Example Costs:**
- 1,000 words (~5,000 characters) = $0.075
- 10,000 words (~50,000 characters) = $0.75

**Cost Comparison:**
- **OpenAI**: High quality, $0.015/1K chars
- **ElevenLabs**: Premium quality, ~$0.18/1K chars (varies by plan)
- **Edge TTS**: Free, good quality

## Troubleshooting

### Error: "OpenAI API key not found"

**Solution:**
```powershell
# PowerShell
$env:OPENAI_API_KEY = "your-key"

# Or set in environment variables permanently
```

### Error: "Voice not supported"

**Solution:** Ensure you're using one of the supported voices:
- coral, alloy, echo, fable, onyx, nova, shimmer

### Error: "Model not found"

**Solution:** Make sure your OpenAI API key has access to `gpt-4o-mini-tts`. If not, you can fall back to:
```yaml
model: "tts-1-hd"  # Older model, still works
```

### Poor Voice Quality

**Solutions:**
1. Use more descriptive instructions
2. Try different voice combinations
3. Ensure good source text quality
4. Check audio export format (MP3 quality settings)

## Best Practices

### 1. Match Voice to Content
- **Technical/Professional**: echo + onyx
- **Educational/Learning**: coral + alloy
- **Storytelling/Narrative**: fable + shimmer
- **Casual/Conversational**: nova + coral

### 2. Write Effective Instructions
- Be specific about tone and delivery
- Use analogies ("like a teacher", "like a friend")
- Keep instructions concise (1-2 sentences)
- Test different instructions to find what works

### 3. Test Before Batch Processing
```powershell
# Test with one file first
synthetic-data-kit podcast "test.txt" --audio --tts openai -v

# Listen to output
# Adjust config if needed
# Then batch process
synthetic-data-kit podcast "./data/input/" --audio --tts openai -v
```

### 4. Balance Quality and Cost
- Use Edge TTS for drafts and testing (free)
- Use OpenAI for final production (good quality, reasonable cost)
- Use ElevenLabs for premium projects (best quality, higher cost)

## Related Resources

- [OpenAI TTS Documentation](https://platform.openai.com/docs/guides/text-to-speech)
- [PODCAST_QUICKSTART.md](PODCAST_QUICKSTART.md) - Quick start guide
- [PODCAST_GENERATOR_GUIDE.md](PODCAST_GENERATOR_GUIDE.md) - Complete feature guide
- [synthetic_data_kit/config.yaml](synthetic_data_kit/config.yaml) - Configuration file

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the [PODCAST_GENERATOR_GUIDE.md](PODCAST_GENERATOR_GUIDE.md)
3. Open an issue on GitHub with verbose output (`-v` flag)

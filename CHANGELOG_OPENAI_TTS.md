# Changelog: OpenAI TTS Update

## Summary

Updated the podcast generator to use OpenAI's latest **`gpt-4o-mini-tts`** model with streaming response and voice instructions support.

## Changes Made

### 1. Configuration (`synthetic_data_kit/config.yaml`)

**Before:**
```yaml
openai:
  default_voices:
    question: "echo"
    answer: "shimmer"
  model: "tts-1-hd"
```

**After:**
```yaml
openai:
  default_voices:
    question: "coral"    # New voice: warm, friendly
    answer: "alloy"      # New voice: clear, balanced
  model: "gpt-4o-mini-tts"
  voice_instructions:
    question: "Speak in a curious and engaging tone, as if asking thoughtful questions."
    answer: "Speak in a clear, informative, and friendly tone, as if explaining concepts."
```

### 2. TTS Implementation (`synthetic_data_kit/utils/tts.py`)

**Key Updates:**

1. **Streaming Response Pattern**
   - Changed from `client.audio.speech.create()` to `with_streaming_response.create()`
   - Follows OpenAI's recommended pattern for efficient audio generation

2. **Voice Instructions Support**
   - Added `instructions` parameter to control tone and delivery style
   - Read from config's `voice_instructions` section

3. **New Voice Model**
   - Updated default model from `tts-1-hd` to `gpt-4o-mini-tts`
   - Supports new voices: coral, alloy, echo, fable, onyx, nova, shimmer

**Code Example:**
```python
with client.audio.speech.with_streaming_response.create(
    model="gpt-4o-mini-tts",
    voice=voice,
    input=text,
    instructions=instructions
) as response:
    response.stream_to_file(temp_file)
```

### 3. Documentation Updates

**New Files:**
- `OPENAI_TTS_VOICES.md` - Comprehensive guide to OpenAI TTS voices and configuration

**Updated Files:**
- `PODCAST_QUICKSTART.md` - Added PowerShell commands and gpt-4o-mini-tts references

## New Features

### 1. Voice Instructions
Control the tone and delivery style of each speaker:

```yaml
voice_instructions:
  question: "Speak with enthusiasm and curiosity, like an excited learner."
  answer: "Speak warmly and encouragingly, like a friendly teacher."
```

### 2. New High-Quality Voices

| Voice | Best For |
|-------|----------|
| coral | Warm, friendly narrator |
| alloy | Clear, balanced professional |
| echo | Confident, authoritative |
| fable | Expressive storytelling |
| onyx | Deep, serious analysis |
| nova | Energetic, youthful |
| shimmer | Soft, gentle explanations |

### 3. Streaming Response
- Lower latency (audio starts generating immediately)
- More efficient memory usage
- Better performance for long text

## Benefits

✅ **Better Voice Quality** - New `gpt-4o-mini-tts` model has improved naturalness
✅ **Tone Control** - Instructions parameter allows fine-tuned delivery style
✅ **More Voice Options** - 7 distinct voices to choose from
✅ **Lower Cost** - `gpt-4o-mini-tts` is more cost-effective than `tts-1-hd`
✅ **Streaming Performance** - Faster audio generation with lower latency

## Migration Guide

### For Existing Users

1. **No Action Required** - The update is backward compatible
2. **Recommended**: Test new voices and instructions
3. **Optional**: Customize voice instructions in config

### Testing the Update

```powershell
# Generate a podcast with the new settings
synthetic-data-kit podcast "test.txt" --audio --tts openai -v

# Listen to the output
# data/audio/test_podcast.mp3
```

### Customizing Voices

Edit `synthetic_data_kit/config.yaml`:

```yaml
podcast:
  text_to_speech:
    openai:
      default_voices:
        question: "nova"     # Try different voices
        answer: "echo"
      voice_instructions:
        question: "Your custom instruction for questioner"
        answer: "Your custom instruction for narrator"
```

## Compatibility

### Requirements
- **OpenAI Python SDK**: `openai >= 1.0.0` (streaming response support)
- **API Access**: OpenAI API key with TTS access
- **Model Access**: `gpt-4o-mini-tts` (available to all OpenAI API users)

### Fallback Options
If you need to use the old model:

```yaml
openai:
  model: "tts-1-hd"  # Use old model
  default_voices:
    question: "echo"
    answer: "shimmer"
```

## Cost Comparison

| Model | Cost per 1K chars | Quality |
|-------|-------------------|---------|
| gpt-4o-mini-tts | $0.015 | High |
| tts-1-hd | $0.015 | High |
| tts-1 | $0.015 | Standard |

*Note: Pricing as of October 2025*

## Examples

### Example 1: Professional Podcast
```yaml
openai:
  default_voices:
    question: "echo"
    answer: "onyx"
  voice_instructions:
    question: "Speak with confidence and directness."
    answer: "Speak authoritatively, like a subject matter expert."
```

### Example 2: Casual Learning
```yaml
openai:
  default_voices:
    question: "nova"
    answer: "coral"
  voice_instructions:
    question: "Speak with enthusiasm and curiosity."
    answer: "Speak warmly and encouragingly, like a friendly teacher."
```

### Example 3: Storytelling
```yaml
openai:
  default_voices:
    question: "fable"
    answer: "shimmer"
  voice_instructions:
    question: "Speak expressively with emotional nuance."
    answer: "Speak gently and thoughtfully, like narrating a story."
```

## Troubleshooting

### Issue: "Voice not supported"
**Solution:** Ensure you're using one of the supported voices: coral, alloy, echo, fable, onyx, nova, shimmer

### Issue: "Model not found"
**Solution:** Update your OpenAI Python package: `pip install --upgrade openai`

### Issue: API rate limits
**Solution:** The streaming response helps, but for large batch jobs, consider:
- Adding delays between requests
- Processing in smaller batches
- Using Edge TTS for testing/drafts

## Testing Checklist

- [x] Configuration updated with new model and voices
- [x] Streaming response implementation working
- [x] Voice instructions parameter added
- [x] Documentation created (OPENAI_TTS_VOICES.md)
- [x] Quick start guide updated
- [x] Backward compatibility maintained

## Resources

- [OpenAI TTS Documentation](https://platform.openai.com/docs/guides/text-to-speech)
- [OPENAI_TTS_VOICES.md](OPENAI_TTS_VOICES.md) - Voice guide
- [PODCAST_QUICKSTART.md](PODCAST_QUICKSTART.md) - Quick start
- [synthetic_data_kit/config.yaml](synthetic_data_kit/config.yaml) - Configuration

## Rollback Instructions

If you need to revert to the old implementation:

1. Edit `config.yaml`:
```yaml
openai:
  model: "tts-1-hd"
  default_voices:
    question: "echo"
    answer: "shimmer"
```

2. Remove the `voice_instructions` section (optional, will be ignored)

## Next Steps

1. **Test the new voices** - Try different combinations
2. **Experiment with instructions** - Find the best tone for your content
3. **Share feedback** - Report any issues or suggestions

---

**Updated:** October 2, 2025
**Version:** 1.1.0
**Author:** Synthetic Data Kit Team

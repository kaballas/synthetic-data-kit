# Environment Variables Setup Guide

## Quick Setup

### 1. Create `.env` File

```powershell
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux/Mac
cp .env.example .env
```

### 2. Edit `.env` with Your Keys

Open `.env` in your editor and add your API keys:

```bash
# For LLM dialogue generation
API_ENDPOINT_KEY=your-api-key-here

# For OpenAI TTS (podcast audio)
OPENAI_API_KEY=sk-your-openai-key-here

# For ElevenLabs TTS (optional)
ELEVENLABS_API_KEY=your-elevenlabs-key-here

# For Google Gemini TTS (optional)
GOOGLE_API_KEY=your-google-api-key-here
```

### 3. Verify Setup

```powershell
# Test that environment variables are loaded
synthetic-data-kit podcast test.txt --audio --tts openai -v
```

## Environment Variable Reference

### Required Keys

#### `API_ENDPOINT_KEY`
- **Used by**: All LLM operations (QA generation, dialogue generation, etc.)
- **Provider**: Your LLM API endpoint (configured in `config.yaml`)
- **Required for**: All synthetic data generation commands

#### `OPENAI_API_KEY`
- **Used by**: OpenAI TTS (podcast audio generation)
- **Format**: `sk-...` (starts with "sk-")
- **Get from**: [OpenAI Platform](https://platform.openai.com/api-keys)
- **Required for**: `--tts openai` flag

### Optional Keys

#### `ELEVENLABS_API_KEY`
- **Used by**: ElevenLabs TTS (premium podcast audio)
- **Get from**: [ElevenLabs](https://elevenlabs.io/)
- **Required for**: `--tts elevenlabs` flag

#### `GOOGLE_API_KEY`
- **Used by**: Google Gemini TTS
- **Get from**: [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Required for**: `--tts gemini` or `--tts geminimulti` flags

### No Key Required

#### Edge TTS
- **Used by**: Free Microsoft Edge TTS
- **No API key needed**: Completely free
- **Usage**: `--tts edge` flag

## Platform-Specific Instructions

### Windows (PowerShell)

#### Set for Current Session
```powershell
$env:OPENAI_API_KEY = "sk-your-key-here"
$env:API_ENDPOINT_KEY = "your-key-here"
```

#### Set Permanently (User Level)
```powershell
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-your-key-here', 'User')
[System.Environment]::SetEnvironmentVariable('API_ENDPOINT_KEY', 'your-key-here', 'User')
```

#### Verify
```powershell
echo $env:OPENAI_API_KEY
echo $env:API_ENDPOINT_KEY
```

### Linux/Mac (Bash/Zsh)

#### Set for Current Session
```bash
export OPENAI_API_KEY="sk-your-key-here"
export API_ENDPOINT_KEY="your-key-here"
```

#### Set Permanently
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.bashrc
echo 'export API_ENDPOINT_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

#### Verify
```bash
echo $OPENAI_API_KEY
echo $API_ENDPOINT_KEY
```

## Using `.env` File (Recommended)

### Advantages
✅ Keep all keys in one place
✅ Easy to manage multiple environments
✅ Automatically loaded by the application
✅ Never committed to git (in `.gitignore`)

### Setup Steps

1. **Copy template**:
   ```powershell
   Copy-Item .env.example .env
   ```

2. **Edit `.env`**:
   ```bash
   # Open in your editor
   notepad .env          # Windows
   nano .env             # Linux
   code .env             # VS Code
   ```

3. **Add your keys**:
   ```bash
   API_ENDPOINT_KEY=abc123xyz
   OPENAI_API_KEY=sk-proj-...
   ELEVENLABS_API_KEY=ell_...
   ```

4. **Verify it works**:
   ```powershell
   synthetic-data-kit podcast test.txt --audio --tts openai -v
   ```

## Loading Environment Variables

The synthetic-data-kit automatically loads environment variables in this order:

1. **`.env` file** (in project root) - Highest priority
2. **System environment variables** - Fallback
3. **Config file values** - Last resort (not recommended for secrets)

### How It Works

```python
# The SDK checks for keys in this order:
api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("API_ENDPOINT_KEY")
```

## Security Best Practices

### ✅ DO:
- Use `.env` file for local development
- Add `.env` to `.gitignore` (already done)
- Use environment variables in production
- Use secrets management in CI/CD (GitHub Secrets, etc.)
- Rotate keys regularly
- Use different keys for development and production

### ❌ DON'T:
- Commit `.env` to git
- Share your `.env` file
- Put keys in `config.yaml` (use env vars instead)
- Hardcode keys in source code
- Use production keys for testing

## Troubleshooting

### Issue: "API key not found"

**Symptoms:**
```
ValueError: OpenAI API key not found. Set OPENAI_API_KEY or API_ENDPOINT_KEY environment variable.
```

**Solutions:**

1. **Check `.env` file exists**:
   ```powershell
   Test-Path .env  # Should return True
   ```

2. **Check key is set correctly** (no quotes in .env):
   ```bash
   # Correct
   OPENAI_API_KEY=sk-proj-abc123

   # Wrong (don't use quotes)
   OPENAI_API_KEY="sk-proj-abc123"
   ```

3. **Verify key is loaded**:
   ```powershell
   # Windows
   echo $env:OPENAI_API_KEY

   # Linux/Mac
   echo $OPENAI_API_KEY
   ```

4. **Restart your terminal** after setting environment variables

### Issue: "Rate limit exceeded"

**Solution:**
- Check your API key has sufficient quota
- Add delays between requests in batch processing
- Use free Edge TTS for testing

### Issue: "Invalid API key"

**Solutions:**
1. Verify the key format:
   - OpenAI: Starts with `sk-proj-` or `sk-`
   - ElevenLabs: Starts with `ell_`
2. Check for extra spaces or newlines
3. Regenerate the key from the provider's dashboard

### Issue: Keys not loading from `.env`

**Solutions:**

1. **Check file location** (must be in project root):
   ```powershell
   Get-Item .env
   # Should show: C:\DTT\synthetic-data-kit\.env
   ```

2. **Check file format** (must be plain text, not .txt extension)

3. **Manual load** (if automatic loading fails):
   ```powershell
   # PowerShell
   Get-Content .env | ForEach-Object {
       if ($_ -match '^([^=]+)=(.*)$') {
           [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
       }
   }
   ```

## Examples

### Example 1: Using OpenAI TTS

```powershell
# 1. Set key (one-time)
$env:OPENAI_API_KEY = "sk-proj-your-key"

# 2. Generate podcast with OpenAI voices
synthetic-data-kit podcast document.txt --audio --tts openai -v

# Output: Uses coral and alloy voices with gpt-4o-mini-tts
```

### Example 2: Using Multiple TTS Providers

```bash
# In .env file:
OPENAI_API_KEY=sk-proj-...
ELEVENLABS_API_KEY=ell_...

# Use OpenAI
synthetic-data-kit podcast doc1.txt --audio --tts openai

# Use ElevenLabs
synthetic-data-kit podcast doc2.txt --audio --tts elevenlabs

# Use Edge (free, no key needed)
synthetic-data-kit podcast doc3.txt --audio --tts edge
```

### Example 3: CI/CD Environment

```yaml
# GitHub Actions example
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  API_ENDPOINT_KEY: ${{ secrets.API_ENDPOINT_KEY }}

steps:
  - name: Generate Podcast
    run: |
      synthetic-data-kit podcast input.txt --audio --tts openai
```

## Advanced Configuration

### Using Python-dotenv (Alternative)

If automatic loading doesn't work, you can manually load `.env`:

```python
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Access variables
api_key = os.getenv("OPENAI_API_KEY")
```

Install python-dotenv:
```powershell
pip install python-dotenv
```

### Multiple Environments

```bash
# Development
.env.development

# Production
.env.production

# Test
.env.test

# Load specific environment
export ENV=production
# Your app can load .env.${ENV}
```

## Related Documentation

- [PODCAST_QUICKSTART.md](PODCAST_QUICKSTART.md) - Quick start guide
- [OPENAI_TTS_VOICES.md](OPENAI_TTS_VOICES.md) - OpenAI TTS voice guide
- [PODCAST_GENERATOR_GUIDE.md](PODCAST_GENERATOR_GUIDE.md) - Complete podcast guide
- [config.yaml](synthetic_data_kit/config.yaml) - Configuration reference

## Support

For issues with environment variables:
1. Check this guide's troubleshooting section
2. Verify your `.env` file format
3. Test with verbose flag: `-v`
4. Open an issue on GitHub with your setup details (don't include actual keys!)

---

**Last Updated:** October 2, 2025

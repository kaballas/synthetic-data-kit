# Environment Variables Update Summary

## What Changed

Added comprehensive environment variable support for API keys and sensitive credentials.

## New Files Created

1. **`.env.example`** - Template for environment variables
   - Contains all API keys with placeholder values
   - Safe to commit to git
   - Copy to `.env` and fill in actual keys

2. **`ENV_SETUP.md`** - Complete environment setup guide
   - Platform-specific instructions (Windows/Linux/Mac)
   - Troubleshooting guide
   - Security best practices
   - Multiple examples

## Updated Files

1. **`README.md`**
   - Added "Environment Variables Setup" section
   - References ENV_SETUP.md
   - Shows recommended .env approach

2. **`PODCAST_QUICKSTART.md`**
   - Added .env setup as recommended approach
   - References ENV_SETUP.md
   - Kept direct env var setting as alternative

## Quick Setup Instructions

### For Users

```bash
# 1. Copy the template
cp .env.example .env

# 2. Edit .env file with your actual keys
# Linux/Mac
nano .env

# Windows
notepad .env

# 3. Add your keys (no quotes needed):
API_ENDPOINT_KEY=your-api-key
OPENAI_API_KEY=sk-your-openai-key
ELEVENLABS_API_KEY=your-elevenlabs-key
GOOGLE_API_KEY=your-google-key

# 4. Use the tools normally - keys are auto-loaded
synthetic-data-kit podcast test.txt --audio --tts openai -v
```

## Supported Environment Variables

| Variable | Used By | Required For |
|----------|---------|--------------|
| `API_ENDPOINT_KEY` | LLM operations | All data generation |
| `OPENAI_API_KEY` | OpenAI TTS | `--tts openai` |
| `ELEVENLABS_API_KEY` | ElevenLabs TTS | `--tts elevenlabs` |
| `GOOGLE_API_KEY` | Gemini TTS | `--tts gemini/geminimulti` |

**Note:** Edge TTS (`--tts edge`) requires no API key - it's free!

## Security Features

✅ `.env` file in `.gitignore` (already configured)
✅ `.env.example` is safe to commit (no actual keys)
✅ Keys loaded automatically by the toolkit
✅ Priority order: `.env` file → system env vars → config file

## Benefits

1. **Security**: Keys not hardcoded in source or config files
2. **Convenience**: All keys in one place (`.env` file)
3. **Flexibility**: Can override with system environment variables
4. **CI/CD Ready**: Works with GitHub Secrets and other secret managers
5. **Multi-Environment**: Easy to maintain dev/test/prod configurations

## Platform-Specific Quick Commands

### Windows (PowerShell)

```powershell
# Copy template
Copy-Item .env.example .env

# Edit file
notepad .env

# Verify (after editing)
synthetic-data-kit podcast test.txt --audio --tts openai -v
```

### Linux/Mac

```bash
# Copy template
cp .env.example .env

# Edit file
nano .env   # or vim, code, etc.

# Verify (after editing)
synthetic-data-kit podcast test.txt --audio --tts openai -v
```

## Troubleshooting

### Problem: "API key not found"

**Solution 1: Check .env file exists**
```bash
# Should exist in project root
ls -la .env  # Linux/Mac
Test-Path .env  # PowerShell
```

**Solution 2: Check .env format**
```bash
# Correct format (no quotes, no spaces around =)
OPENAI_API_KEY=sk-proj-abc123

# Wrong
OPENAI_API_KEY = "sk-proj-abc123"
```

**Solution 3: Restart terminal**
After setting environment variables, restart your terminal or IDE.

### Problem: Keys not loading

**Check file location:**
```bash
# Must be in project root where you run commands
pwd  # Should show: /path/to/synthetic-data-kit
```

### Problem: Still can't find keys

**Manual load (PowerShell):**
```powershell
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
    }
}
```

## Migration Guide

### If you had keys in config.yaml

**Before:**
```yaml
api-endpoint:
  api_key: "my-secret-key"  # ❌ Not recommended
```

**After:**
```yaml
api-endpoint:
  api_key: null  # Use API_ENDPOINT_KEY env var instead
```

```bash
# In .env file
API_ENDPOINT_KEY=my-secret-key
```

## Documentation Links

- **[ENV_SETUP.md](ENV_SETUP.md)** - Complete environment setup guide
- **[.env.example](.env.example)** - Template file
- **[README.md](README.md)** - Main documentation
- **[PODCAST_QUICKSTART.md](PODCAST_QUICKSTART.md)** - Podcast quick start

## Testing Checklist

- [x] `.env.example` created with all keys
- [x] `ENV_SETUP.md` created with comprehensive guide
- [x] `README.md` updated with env var section
- [x] `PODCAST_QUICKSTART.md` updated with .env approach
- [x] `.gitignore` already contains `.env` (verified)
- [ ] Users test with actual keys

## Next Steps for Users

1. **Copy template**: `cp .env.example .env`
2. **Add keys**: Edit `.env` with your actual API keys
3. **Test**: Run a command to verify keys are loaded
4. **Secure**: Never commit `.env` to git (already in .gitignore)

## Support

If you have issues with environment variables:
1. Check [ENV_SETUP.md](ENV_SETUP.md) troubleshooting section
2. Verify `.env` file format (no quotes, no spaces)
3. Restart terminal/IDE after changes
4. Use verbose flag: `-v` for more details

---

**Date:** October 2, 2025  
**Impact:** All commands that use API keys  
**Breaking Changes:** None (backward compatible)

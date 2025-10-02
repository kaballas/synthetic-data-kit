# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.
# Text-to-Speech utilities for podcast audio generation

import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydub import AudioSegment


def generate_podcast_audio(
    dialogue: List[Dict[str, str]],
    base_name: str,
    tts_provider: str,
    config: Dict[str, Any],
    verbose: bool = False
) -> str:
    """Generate audio file from podcast dialogue
    
    Args:
        dialogue: List of dialogue turns with speaker and text
        base_name: Base name for output file
        tts_provider: TTS provider to use (openai, elevenlabs, edge, gemini, geminimulti)
        config: Configuration dictionary
        verbose: Show detailed progress
    
    Returns:
        Path to generated audio file
    """
    podcast_config = config.get("podcast", {})
    tts_config = podcast_config.get("text_to_speech", {})
    
    # Get output directories
    audio_dir = tts_config.get("output_directories", {}).get("audio", "./data/audio")
    temp_dir = tts_config.get("temp_audio_dir", "data/audio/tmp/")
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)
    
    # Get audio format
    audio_format = tts_config.get("audio_format", "mp3")
    
    if verbose:
        print(f"Generating podcast audio using {tts_provider}...")
    
    # Generate audio based on provider
    if tts_provider == "openai":
        audio_path = _generate_openai_audio(dialogue, base_name, audio_dir, temp_dir, tts_config, audio_format, verbose)
    elif tts_provider == "elevenlabs":
        audio_path = _generate_elevenlabs_audio(dialogue, base_name, audio_dir, temp_dir, tts_config, audio_format, verbose)
    elif tts_provider == "edge":
        audio_path = _generate_edge_audio(dialogue, base_name, audio_dir, temp_dir, tts_config, audio_format, verbose)
    elif tts_provider == "gemini":
        audio_path = _generate_gemini_audio(dialogue, base_name, audio_dir, temp_dir, tts_config, audio_format, verbose)
    elif tts_provider == "geminimulti":
        audio_path = _generate_gemini_multi_audio(dialogue, base_name, audio_dir, temp_dir, tts_config, audio_format, verbose)
    else:
        raise ValueError(f"Unsupported TTS provider: {tts_provider}")
    
    if verbose:
        print(f"Audio generated: {audio_path}")
    
    return audio_path


def _generate_openai_audio(
    dialogue: List[Dict[str, str]],
    base_name: str,
    audio_dir: str,
    temp_dir: str,
    tts_config: Dict[str, Any],
    audio_format: str,
    verbose: bool
) -> str:
    """Generate audio using OpenAI TTS"""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("OpenAI package not installed. Install with: pip install openai")
    
    openai_config = tts_config.get("openai", {})
    voices = openai_config.get("default_voices", {})
    voice_instructions = openai_config.get("voice_instructions", {})
    model = openai_config.get("model", "gpt-4o-mini-tts")
    
    # Get API key from environment or config
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("API_ENDPOINT_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY or API_ENDPOINT_KEY environment variable.")
    
    client = OpenAI(api_key=api_key)
    
    # Generate audio segments
    audio_segments = []
    
    for i, turn in enumerate(dialogue):
        speaker = turn.get("speaker", "Person1")
        text = turn.get("text", "")
        
        if not text:
            continue
        
        # Map speaker to voice and instructions
        # Person1 = main speaker (answer), Person2 = questioner (question)
        speaker_type = "answer" if speaker == "Person1" else "question"
        voice = voices.get(speaker_type, "alloy")
        instructions = voice_instructions.get(speaker_type, "Speak in a natural and engaging tone.")
        
        if verbose:
            print(f"  Generating audio for turn {i+1}/{len(dialogue)} ({speaker}, voice: {voice})...")
        
        # Generate speech with streaming response and instructions
        temp_file = os.path.join(temp_dir, f"{base_name}_turn_{i}.mp3")
        
        with client.audio.speech.with_streaming_response.create(
            model=model,
            voice=voice,
            input=text,
            instructions=instructions
        ) as response:
            response.stream_to_file(temp_file)
        
        # Load audio segment
        segment = AudioSegment.from_mp3(temp_file)
        audio_segments.append(segment)
        
        # Add small pause between turns (500ms)
        if i < len(dialogue) - 1:
            audio_segments.append(AudioSegment.silent(duration=500))
    
    # Combine all segments
    combined = sum(audio_segments)
    
    # Export final audio
    output_path = os.path.join(audio_dir, f"{base_name}_podcast.{audio_format}")
    combined.export(output_path, format=audio_format)
    
    # Cleanup temp files
    for file in Path(temp_dir).glob(f"{base_name}_turn_*.mp3"):
        file.unlink()
    
    return output_path


def _generate_elevenlabs_audio(
    dialogue: List[Dict[str, str]],
    base_name: str,
    audio_dir: str,
    temp_dir: str,
    tts_config: Dict[str, Any],
    audio_format: str,
    verbose: bool
) -> str:
    """Generate audio using ElevenLabs TTS"""
    try:
        from elevenlabs import generate, save, Voice
    except ImportError:
        raise ImportError("ElevenLabs package not installed. Install with: pip install elevenlabs")
    
    elevenlabs_config = tts_config.get("elevenlabs", {})
    voices = elevenlabs_config.get("default_voices", {})
    model = elevenlabs_config.get("model", "eleven_multilingual_v2")
    
    # Get API key
    api_key = os.environ.get("ELEVENLABS_API_KEY") or elevenlabs_config.get("api_key")
    if not api_key:
        raise ValueError("ElevenLabs API key not found. Set ELEVENLABS_API_KEY environment variable.")
    
    os.environ["ELEVENLABS_API_KEY"] = api_key
    
    audio_segments = []
    
    for i, turn in enumerate(dialogue):
        speaker = turn.get("speaker", "Person1")
        text = turn.get("text", "")
        
        if not text:
            continue
        
        # Map speaker to voice
        voice = voices.get("answer" if speaker == "Person1" else "question", "Chris")
        
        if verbose:
            print(f"  Generating audio for turn {i+1}/{len(dialogue)} ({speaker})...")
        
        # Generate speech
        audio = generate(text=text, voice=voice, model=model)
        
        temp_file = os.path.join(temp_dir, f"{base_name}_turn_{i}.mp3")
        save(audio, temp_file)
        
        # Load audio segment
        segment = AudioSegment.from_mp3(temp_file)
        audio_segments.append(segment)
        
        # Add small pause between turns
        if i < len(dialogue) - 1:
            audio_segments.append(AudioSegment.silent(duration=500))
    
    # Combine all segments
    combined = sum(audio_segments)
    
    # Export final audio
    output_path = os.path.join(audio_dir, f"{base_name}_podcast.{audio_format}")
    combined.export(output_path, format=audio_format)
    
    # Cleanup
    for file in Path(temp_dir).glob(f"{base_name}_turn_*.mp3"):
        file.unlink()
    
    return output_path


def _generate_edge_audio(
    dialogue: List[Dict[str, str]],
    base_name: str,
    audio_dir: str,
    temp_dir: str,
    tts_config: Dict[str, Any],
    audio_format: str,
    verbose: bool
) -> str:
    """Generate audio using Edge TTS (free, no API key needed)"""
    try:
        import edge_tts
        import asyncio
    except ImportError:
        raise ImportError("Edge TTS package not installed. Install with: pip install edge-tts")
    
    edge_config = tts_config.get("edge", {})
    voices = edge_config.get("default_voices", {})
    
    audio_segments = []
    
    async def generate_speech(text, voice, output_file):
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
    
    for i, turn in enumerate(dialogue):
        speaker = turn.get("speaker", "Person1")
        text = turn.get("text", "")
        
        if not text:
            continue
        
        # Map speaker to voice
        voice = voices.get("answer" if speaker == "Person1" else "question", "en-US-JennyNeural")
        
        if verbose:
            print(f"  Generating audio for turn {i+1}/{len(dialogue)} ({speaker})...")
        
        # Generate speech
        temp_file = os.path.join(temp_dir, f"{base_name}_turn_{i}.mp3")
        asyncio.run(generate_speech(text, voice, temp_file))
        
        # Load audio segment
        segment = AudioSegment.from_mp3(temp_file)
        audio_segments.append(segment)
        
        # Add small pause between turns
        if i < len(dialogue) - 1:
            audio_segments.append(AudioSegment.silent(duration=500))
    
    # Combine all segments
    combined = sum(audio_segments)
    
    # Export final audio
    output_path = os.path.join(audio_dir, f"{base_name}_podcast.{audio_format}")
    combined.export(output_path, format=audio_format)
    
    # Cleanup
    for file in Path(temp_dir).glob(f"{base_name}_turn_*.mp3"):
        file.unlink()
    
    return output_path


def _generate_gemini_audio(
    dialogue: List[Dict[str, str]],
    base_name: str,
    audio_dir: str,
    temp_dir: str,
    tts_config: Dict[str, Any],
    audio_format: str,
    verbose: bool
) -> str:
    """Generate audio using Google Gemini TTS"""
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError("Google Generative AI package not installed. Install with: pip install google-generativeai")
    
    gemini_config = tts_config.get("gemini", {})
    voices = gemini_config.get("default_voices", {})
    
    # Get API key
    api_key = os.environ.get("GOOGLE_API_KEY") or gemini_config.get("api_key")
    if not api_key:
        raise ValueError("Google API key not found. Set GOOGLE_API_KEY environment variable.")
    
    genai.configure(api_key=api_key)
    
    audio_segments = []
    
    for i, turn in enumerate(dialogue):
        speaker = turn.get("speaker", "Person1")
        text = turn.get("text", "")
        
        if not text:
            continue
        
        # Map speaker to voice
        voice = voices.get("answer" if speaker == "Person1" else "question", "en-US-Journey-D")
        
        if verbose:
            print(f"  Generating audio for turn {i+1}/{len(dialogue)} ({speaker})...")
        
        # Note: This is a placeholder - actual Gemini TTS API may differ
        # You'll need to update this based on the actual Gemini TTS API
        print(f"Warning: Gemini TTS integration is placeholder. Implement based on actual API.")
        
        # For now, fallback or skip
        continue
    
    # If no audio was generated, raise error
    if not audio_segments:
        raise NotImplementedError("Gemini TTS is not fully implemented yet")
    
    return ""


def _generate_gemini_multi_audio(
    dialogue: List[Dict[str, str]],
    base_name: str,
    audio_dir: str,
    temp_dir: str,
    tts_config: Dict[str, Any],
    audio_format: str,
    verbose: bool
) -> str:
    """Generate audio using Google Gemini Multi-speaker TTS"""
    # Placeholder for Gemini Multi-speaker implementation
    print("Warning: Gemini Multi-speaker TTS not yet implemented")
    return _generate_gemini_audio(dialogue, base_name, audio_dir, temp_dir, tts_config, audio_format, verbose)

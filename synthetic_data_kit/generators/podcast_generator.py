# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.
# Podcast generation logic - converts text to conversational podcast format

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from synthetic_data_kit.models.llm_client import LLMClient
from synthetic_data_kit.utils.config import get_generation_config
from synthetic_data_kit.utils.text import split_into_chunks


class PodcastGenerator:
    """Generates conversational podcast dialogues from text"""
    
    def __init__(self, client: LLMClient, config_path: Optional[Path] = None):
        """Initialize the Podcast Generator with an LLM client and optional config"""
        self.client = client
        self.config = client.config
        self.podcast_config = self.config.get("podcast", {})
        self.generation_config = get_generation_config(self.config)
    
    def _get_podcast_generation_prompt(self, text: str, chunk_index: int = 0, total_chunks: int = 1) -> str:
        """Generate the prompt for podcast dialogue creation"""
        
        conversation_style = ", ".join(self.podcast_config.get("conversation_style", ["engaging"]))
        person1_role = self.podcast_config.get("roles", {}).get("person1", "main summarizer")
        person2_role = self.podcast_config.get("roles", {}).get("person2", "questioner/clarifier")
        podcast_name = self.podcast_config.get("podcast_name", "PODCASTIFY")
        podcast_tagline = self.podcast_config.get("podcast_tagline", "Your Personal Generative AI Podcast")
        engagement_techniques = ", ".join(self.podcast_config.get("engagement_techniques", ["rhetorical questions"]))
        user_instructions = self.podcast_config.get("user_instructions", "")
        
        # Determine section based on chunk
        if total_chunks == 1:
            section = "full podcast"
        elif chunk_index == 0:
            section = "Introduction"
        elif chunk_index == total_chunks - 1:
            section = "Conclusion"
        else:
            section = f"Main Content Part {chunk_index}"
        
        prompt = f"""You are creating a podcast dialogue for "{podcast_name}" - {podcast_tagline}.

Generate a {conversation_style} conversation between two speakers for the {section} section.

SPEAKER ROLES:
- Speaker 1 (Person1): {person1_role}
- Speaker 2 (Person2): {person2_role}

ENGAGEMENT TECHNIQUES TO USE:
{engagement_techniques}

CONVERSATION GUIDELINES:
1. Keep the dialogue natural and conversational
2. Break down complex concepts into digestible explanations
3. Use {conversation_style} tone throughout
4. Speaker 2 should ask clarifying questions to help listeners understand
5. Include transitions between topics
6. Keep each speaker's turn to 2-4 sentences maximum
7. Alternate between speakers frequently

{f'ADDITIONAL INSTRUCTIONS: {user_instructions}' if user_instructions else ''}

SOURCE CONTENT:
{text}

Generate the dialogue in this JSON format:
{{
  "dialogue": [
    {{
      "speaker": "Person1",
      "text": "..."
    }},
    {{
      "speaker": "Person2",
      "text": "..."
    }}
  ]
}}

Return ONLY the JSON, no additional text."""
        
        return prompt
    
    def _parse_dialogue_response(self, response: str) -> List[Dict[str, str]]:
        """Parse the LLM response into dialogue format"""
        verbose = os.environ.get('SDK_VERBOSE', 'false').lower() == 'true'
        
        # Try to extract JSON
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                if "dialogue" in data and isinstance(data["dialogue"], list):
                    return data["dialogue"]
            except json.JSONDecodeError as e:
                if verbose:
                    print(f"Failed to parse dialogue JSON: {e}")
        
        # Fallback: try to parse line by line
        dialogue = []
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Try to match "Person1: text" or "Speaker 1: text" format
            match = re.match(r'(Person[12]|Speaker [12]):\s*(.+)', line)
            if match:
                speaker = "Person1" if "1" in match.group(1) else "Person2"
                text = match.group(2).strip()
                dialogue.append({"speaker": speaker, "text": text})
        
        return dialogue if dialogue else []
    
    def generate_podcast_dialogue(
        self,
        text: str,
        num_chunks: Optional[int] = None,
        verbose: bool = False
    ) -> List[Dict[str, str]]:
        """Generate podcast dialogue from text
        
        Args:
            text: Source text to convert to podcast
            num_chunks: Number of dialogue chunks to generate (for long content)
            verbose: Show detailed progress
        
        Returns:
            List of dialogue turns with speaker and text
        """
        # Get chunking parameters
        max_chunks = self.podcast_config.get("max_num_chunks", 8)
        min_chunk_size = self.podcast_config.get("min_chunk_size", 600)
        chunk_size = self.generation_config.get("chunk_size", 4000)
        
        if num_chunks is None:
            num_chunks = min(max_chunks, max(1, len(text) // chunk_size))
        
        # Split text into chunks if needed
        if len(text) > chunk_size:
            text_chunks = split_into_chunks(text, chunk_size=chunk_size, overlap=200)
            if verbose:
                print(f"Split text into {len(text_chunks)} chunks for podcast generation")
        else:
            text_chunks = [text]
        
        # Limit number of chunks
        text_chunks = text_chunks[:num_chunks]
        
        all_dialogue = []
        
        # Generate dialogue for each chunk
        for i, chunk in enumerate(text_chunks):
            if verbose:
                print(f"Generating dialogue for chunk {i+1}/{len(text_chunks)}...")
            
            prompt = self._get_podcast_generation_prompt(chunk, i, len(text_chunks))
            
            # Generate dialogue
            temperature = self.podcast_config.get("creativity", 1) * 0.5 + 0.5  # Convert 0-2 to 0.5-1.5
            max_tokens = self.generation_config.get("max_tokens", 4096)
            
            messages = [{"role": "system", "content": prompt}]
            response = self.client.chat_completion(
                messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Parse response
            dialogue_chunk = self._parse_dialogue_response(response)
            
            if dialogue_chunk:
                all_dialogue.extend(dialogue_chunk)
                if verbose:
                    print(f"  Generated {len(dialogue_chunk)} dialogue turns")
            else:
                if verbose:
                    print(f"  Warning: Failed to generate dialogue for chunk {i+1}")
        
        # Add ending message if configured
        ending_message = self.podcast_config.get("text_to_speech", {}).get("ending_message")
        if ending_message:
            all_dialogue.append({"speaker": "Person1", "text": ending_message})
        
        return all_dialogue
    
    def format_transcript(self, dialogue: List[Dict[str, str]], include_timestamps: bool = False) -> str:
        """Format dialogue as a readable transcript
        
        Args:
            dialogue: List of dialogue turns
            include_timestamps: Whether to include timestamp placeholders
        
        Returns:
            Formatted transcript text
        """
        podcast_name = self.podcast_config.get("podcast_name", "PODCASTIFY")
        podcast_tagline = self.podcast_config.get("podcast_tagline", "Your Personal Generative AI Podcast")
        
        transcript = f"=== {podcast_name} ===\n"
        transcript += f"{podcast_tagline}\n\n"
        transcript += "=" * 50 + "\n\n"
        
        timestamp = 0
        for turn in dialogue:
            speaker = turn.get("speaker", "Unknown")
            text = turn.get("text", "")
            
            if include_timestamps:
                minutes = timestamp // 60
                seconds = timestamp % 60
                transcript += f"[{minutes:02d}:{seconds:02d}] {speaker}: {text}\n\n"
                # Estimate ~3 seconds per sentence
                timestamp += len(text.split('.')) * 3
            else:
                transcript += f"{speaker}: {text}\n\n"
        
        return transcript
    
    def save_transcript(self, dialogue: List[Dict[str, str]], output_path: str, verbose: bool = False) -> str:
        """Save podcast transcript to file
        
        Args:
            dialogue: List of dialogue turns
            output_path: Path to save transcript
            verbose: Show detailed output
        
        Returns:
            Path to saved transcript
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Format and save transcript
        transcript = self.format_transcript(dialogue, include_timestamps=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(transcript)
        
        if verbose:
            print(f"Transcript saved to: {output_path}")
        
        return output_path
    
    def process_document(
        self,
        document_text: str,
        output_dir: str,
        base_name: str,
        generate_audio: bool = False,
        tts_provider: Optional[str] = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Process a document to generate podcast dialogue and optionally audio
        
        Args:
            document_text: Source text
            output_dir: Directory to save outputs
            base_name: Base filename for outputs
            generate_audio: Whether to generate audio files
            tts_provider: TTS provider to use (if generating audio)
            verbose: Show detailed progress
        
        Returns:
            Dictionary with paths to generated files
        """
        # Generate dialogue
        if verbose:
            print(f"Generating podcast dialogue from document...")
        
        dialogue = self.generate_podcast_dialogue(document_text, verbose=verbose)
        
        if not dialogue:
            raise ValueError("Failed to generate podcast dialogue")
        
        # Save transcript
        transcript_dir = self.podcast_config.get("text_to_speech", {}).get(
            "output_directories", {}
        ).get("transcripts", "./data/transcripts")
        
        os.makedirs(transcript_dir, exist_ok=True)
        transcript_path = os.path.join(transcript_dir, f"{base_name}_podcast_transcript.txt")
        self.save_transcript(dialogue, transcript_path, verbose)
        
        # Save dialogue JSON
        dialogue_path = os.path.join(output_dir, f"{base_name}_podcast_dialogue.json")
        os.makedirs(output_dir, exist_ok=True)
        with open(dialogue_path, 'w', encoding='utf-8') as f:
            json.dump({"dialogue": dialogue, "metadata": {"turns": len(dialogue)}}, f, indent=2)
        
        result = {
            "transcript_path": transcript_path,
            "dialogue_path": dialogue_path,
            "num_turns": len(dialogue)
        }
        
        # Generate audio if requested
        if generate_audio:
            try:
                from synthetic_data_kit.utils.tts import generate_podcast_audio
                
                audio_path = generate_podcast_audio(
                    dialogue,
                    base_name,
                    tts_provider or self.podcast_config.get("text_to_speech", {}).get("default_tts_model", "openai"),
                    self.config,
                    verbose
                )
                result["audio_path"] = audio_path
            except ImportError:
                print("Warning: TTS module not available. Skipping audio generation.")
            except Exception as e:
                print(f"Warning: Failed to generate audio: {e}")
        
        if verbose:
            print(f"Podcast generation complete!")
            print(f"  Turns: {len(dialogue)}")
            print(f"  Transcript: {transcript_path}")
            print(f"  Dialogue: {dialogue_path}")
        
        return result

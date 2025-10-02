# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.
# Core podcast processing logic

import os
from pathlib import Path
from typing import Optional, Dict, Any

from synthetic_data_kit.models.llm_client import LLMClient
from synthetic_data_kit.generators.podcast_generator import PodcastGenerator


def read_text_file(file_path: str) -> str:
    """Read text file content"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def process_file(
    file_path: str,
    output_dir: str,
    config_path: Optional[Path] = None,
    api_base: Optional[str] = None,
    model: Optional[str] = None,
    generate_audio: bool = False,
    tts_provider: Optional[str] = None,
    num_chunks: Optional[int] = None,
    verbose: bool = False,
    provider: Optional[str] = None,
) -> Dict[str, Any]:
    """Process a file to generate podcast
    
    Args:
        file_path: Path to the text file to process
        output_dir: Directory to save generated content
        config_path: Path to configuration file
        api_base: API base URL
        model: Model to use
        generate_audio: Whether to generate audio file
        tts_provider: TTS provider to use
        num_chunks: Number of dialogue chunks
        verbose: Show detailed output
        provider: LLM provider to use
    
    Returns:
        Dictionary with paths to generated files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize LLM client
    client = LLMClient(
        config_path=config_path,
        provider=provider,
        api_base=api_base,
        model_name=model
    )
    
    if verbose:
        print(f"Using {client.provider} provider for podcast generation")
    
    # Read document text
    document_text = read_text_file(file_path)
    
    # Generate base filename for output
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    
    # Initialize podcast generator
    generator = PodcastGenerator(client, config_path)
    
    # Process document
    result = generator.process_document(
        document_text,
        output_dir,
        base_name,
        generate_audio,
        tts_provider,
        verbose
    )
    
    return result

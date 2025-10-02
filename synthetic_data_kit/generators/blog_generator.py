# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.
# Create Blog Posts

from typing import Dict, List, Any, Optional
import json
import os
from pathlib import Path

from synthetic_data_kit.models.llm_client import LLMClient
from synthetic_data_kit.utils.text import split_into_chunks
from synthetic_data_kit.utils.config import load_config, get_generation_config, get_prompt


class BlogGenerator:
    def __init__(self, 
                 client: LLMClient,
                 config_path: Optional[Path] = None):
        """Initialize the Blog Generator with an LLM client and optional config"""
        self.client = client
        
        # Load config
        self.config = load_config(config_path)
        
        # Get specific configurations
        self.generation_config = get_generation_config(self.config)

    def generate_blog_post(self, 
                         document_text: str, 
                         title: Optional[str] = None,
                         max_tokens: Optional[int] = None) -> Dict[str, str]:
        """Generate a blog post from the document text"""
        verbose = os.environ.get('SDK_VERBOSE', 'false').lower() == 'true'
        
        if verbose:
            print("Generating blog post...")
        
        # Get generation config
        temperature = self.generation_config.get("temperature", 0.7)
        max_tokens = max_tokens or self.generation_config.get("max_tokens", 4096)
        
        # Get blog post generation prompt
        blog_prompt_template = get_prompt(self.config, "blog_generation")
        
        # Format the prompt with the document text
        blog_prompt = blog_prompt_template.format(
            document_text=document_text,
            title=title or "Blog Post"
        )
        
        messages = [
            {"role": "system", "content": blog_prompt}
        ]
        
        # Generate the blog post
        response = self.client.chat_completion(
            messages, 
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        if verbose:
            print(f"Blog post generated ({len(response)} chars)")
        
        # Parse the response into a structured format
        blog_post = {
            "title": title or self.extract_title(response),
            "content": response,
            "word_count": len(response.split())
        }
        
        return blog_post

    def extract_title(self, content: str) -> str:
        """Extract or generate a title from the content"""
        # Simple approach: take the first sentence or first 10 words as title
        # More sophisticated approaches could be implemented
        sentences = content.split('.')
        if sentences and sentences[0]:
            title = sentences[0].strip()
            # Limit to 10 words max
            title_words = title.split()[:10]
            return ' '.join(title_words)
        return "Generated Blog Post"

    def generate_blog_from_chunks(self, 
                                document_text: str, 
                                title: Optional[str] = None,
                                chunk_size: Optional[int] = None,
                                overlap: Optional[int] = None) -> Dict[str, str]:
        """Generate a blog post by processing document in chunks for longer documents"""
        verbose = os.environ.get('SDK_VERBOSE', 'false').lower() == 'true'
        
        # Get generation config
        chunk_size = chunk_size or self.generation_config.get("chunk_size", 4000)
        overlap = overlap or self.generation_config.get("overlap", 200)
        
        # Split text into chunks
        chunks = split_into_chunks(
            document_text, 
            chunk_size=chunk_size, 
            overlap=overlap
        )
        
        if verbose:
            print(f"Processing document in {len(chunks)} chunks for blog generation")
        
        blog_parts = []
        for i, chunk in enumerate(chunks):
            if verbose:
                print(f"Processing chunk {i+1}/{len(chunks)} for blog generation")
            
            # Generate blog section from this chunk
            blog_section = self.generate_blog_post(chunk, f"{title} - Part {i+1}")
            blog_parts.append(blog_section["content"])
        
        # Combine all parts into a single blog post
        full_content = "\n\n---\n\n".join(blog_parts)
        
        blog_post = {
            "title": title or "Generated Blog Post",
            "content": full_content,
            "word_count": len(full_content.split()),
            "sections": len(chunks)
        }
        
        return blog_post

    def process_documents(self,
                        documents: List[Dict[str, Any]],
                        title: Optional[str] = None,
                        verbose: bool = False) -> Dict[str, Any]:
        """Process a list of documents to generate a blog post"""
        # Set the verbose environment variable
        if verbose:
            os.environ['SDK_VERBOSE'] = 'true'
        else:
            os.environ['SDK_VERBOSE'] = 'false'

        full_text = " ".join([doc["text"] for doc in documents if doc["text"]])

        # Generate the blog post
        blog_post = self.generate_blog_from_chunks(full_text, title)

        result = {
            "blog_post": blog_post
        }

        return result
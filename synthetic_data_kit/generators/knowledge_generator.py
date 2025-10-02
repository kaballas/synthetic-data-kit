# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.
# Generate knowledge graphs from text using LLM

import json
import re
import logging
import tempfile
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

from synthetic_data_kit.models.llm_client import LLMClient
from synthetic_data_kit.utils.config import load_config


class KnowledgeGraphGenerator:
    def __init__(self, client: LLMClient, config_path: Optional[Path] = None, debug: bool = False):
        """Initialize the KnowledgeGraphGenerator with an LLM client"""
        self.client = client
        self.config_path = config_path
        self.config = load_config(config_path) if config_path else client.config
        self.debug = debug
        self.logger = logging.getLogger(__name__)
        if self.debug:
            # Configure basic logging if debug mode enabled (caller may configure logging separately)
            logging.basicConfig(level=logging.DEBUG)
            self.logger.setLevel(logging.DEBUG)

    def extract_knowledge_graph(self, text: str, debug: bool = False) -> Dict[str, Any]:
        """Extract a knowledge graph from text using the LLM with the knowledge prompt
        
        Args:
            text: Input text to extract knowledge graph from
            debug: If True, emit extra debugging information and artifacts
            
        Returns:
            Dictionary containing nodes, relationships, and errors as defined in the knowledge prompt
        """
        debug = debug or self.debug
        # Get the knowledge prompt from config
        prompts_config = self.config.get("prompts", {})
        knowledge_prompt = prompts_config.get("knowledge", "")
        
        # Format the prompt with the input text
        try:
            formatted_prompt = knowledge_prompt.format(input=text)
        except Exception as e:
            # Fall back to simple concatenation if formatting fails
            self.logger.debug("Prompt formatting with .format(input=...) failed; falling back to concatenation. Error: %s", e)
            formatted_prompt = f"{knowledge_prompt}\n\nText:\n{text}"
        
        # Log prompt preview
        if debug:
            self.logger.debug("Knowledge prompt length: %d", len(knowledge_prompt))
            self.logger.debug("Formatted prompt preview (first 1000 chars): %s", formatted_prompt[:1000].replace("\n", "\\n"))
        
        # Create messages for the LLM
        messages = [
            {
                "role": "user",
                "content": formatted_prompt
            }
        ]
        
        if debug:
            # Avoid logging full prompt twice but log message role/length
            self.logger.debug("Created %d message(s) for LLM. First message length: %d", len(messages), len(messages[0]["content"]))
        
        # Get generation parameters from config
        generation_config = self.config.get("generation", {})
        temperature = generation_config.get("temperature", 0.7)
        max_tokens = generation_config.get("max_tokens", 4096)
        
        # Generate the knowledge graph using the LLM
        response = self.client.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        if debug:
            self.logger.debug("LLM response length: %d", len(response) if isinstance(response, str) else 0)
            self.logger.debug("LLM response preview (first 2000 chars): %s", (response[:2000] if isinstance(response, str) else str(response)).replace("\n", "\\n"))
        else:
            self.logger.info("Received LLM response (length %d)", len(response) if isinstance(response, str) else 0)

        # Extract JSON from response - the LLM might wrap the JSON in markdown
        json_match = re.search(r'```json\s*\n*(.*?)\n*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            if debug:
                self.logger.debug("Extracted JSON from triple-backtick ```json block; extracted length: %d", len(json_str))
        else:
            # Try to find JSON object in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                if debug:
                    self.logger.debug("Extracted JSON object using brace search; extracted length: %d", len(json_str))
            else:
                # No JSON found - provide debug artifact and raise a descriptive error
                if debug:
                    try:
                        tmpdir = tempfile.mkdtemp(prefix="kg_extraction_")
                        tmp_path = os.path.join(tmpdir, "llm_response.txt")
                        with open(tmp_path, "w", encoding="utf-8") as f:
                            f.write(response)
                        self.logger.debug("No JSON found in LLM response. Saved full response to: %s", tmp_path)
                    except Exception as save_err:
                        self.logger.debug("Failed to save LLM response to temp file: %s", save_err)
                raise ValueError(f"Could not extract JSON from LLM response: {response[:2000]}")

        # Parse the JSON response
        try:
            knowledge_graph = json.loads(json_str)
        except json.JSONDecodeError as e:
            # Save parse artifacts for debugging
            if debug:
                try:
                    tmpdir = tempfile.mkdtemp(prefix="kg_parse_error_")
                    resp_path = os.path.join(tmpdir, "llm_response.txt")
                    json_path = os.path.join(tmpdir, "extracted_json.txt")
                    with open(resp_path, "w", encoding="utf-8") as f:
                        f.write(response)
                    with open(json_path, "w", encoding="utf-8") as f:
                        f.write(json_str)
                    self.logger.debug("JSON parse error. Saved response to %s and extracted fragment to %s", resp_path, json_path)
                except Exception as save_err:
                    self.logger.debug("Failed to save parse artifacts: %s", save_err)
            raise ValueError(f"Could not parse JSON response from LLM: {e}\nExtracted fragment (first 2000 chars): {json_str[:2000]}")
        
        if debug:
            nodes = knowledge_graph.get("nodes", [])
            rels = knowledge_graph.get("relationships", [])
            self.logger.debug("Parsed knowledge graph: nodes=%d relationships=%d", len(nodes), len(rels))
        
        return knowledge_graph

    def process_documents(self, documents: List[Dict[str, Any]], verbose: bool = False) -> Dict[str, Any]:
        """Process a list of documents to generate a knowledge graph
        
        Args:
            documents: List of documents, each with 'text' field or JSON content
            verbose: Whether to print detailed progress information
            
        Returns:
            Dictionary containing the knowledge graph
        """
        # For the knowledge extraction, we want to pass the raw document content to the LLM
        # The LLM will process the content according to the knowledge extraction prompt
        
        # For text documents, combine the text
        combined_text = " ".join([doc.get("text", "") for doc in documents if doc.get("text")])
        
        if not combined_text.strip():
            # If no text content found, try to convert the documents to JSON string format
            try:
                combined_text = json.dumps(documents, ensure_ascii=False)
            except Exception:
                # If that fails, convert each document individually and join them
                combined_texts = []
                for doc in documents:
                    try:
                        combined_texts.append(json.dumps(doc, ensure_ascii=False))
                    except Exception:
                        # Fallback: convert to string representation
                        combined_texts.append(str(doc))
                combined_text = " ".join(combined_texts)
        
        if verbose or self.debug:
            self.logger.info("Processing %d documents with total length: %d characters", len(documents), len(combined_text))
        
        # Extract the knowledge graph from the combined text using the LLM
        knowledge_graph = self.extract_knowledge_graph(combined_text, debug=(verbose or self.debug))
        
        if verbose or self.debug:
            self.logger.info(
                "Extracted knowledge graph with %d nodes and %d relationships",
                len(knowledge_graph.get("nodes", [])),
                len(knowledge_graph.get("relationships", []))
            )
        
        return knowledge_graph
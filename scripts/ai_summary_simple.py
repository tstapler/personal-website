#!/usr/bin/env python3
"""
Simplified AI Summary Generator - Working Implementation
"""

import os
import json
import logging
import sys
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SummaryGenerator:
    """Simplified summary generator without complex imports"""
    
    def __init__(self, config_file: str = "summary_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from file and environment"""
        config = {
            "providers": {
                "openai": {
                    "model": "gpt-3.5-turbo",
                    "api_key": None  # Set via environment variable
                }
            },
            "default_provider": "openai",
            "fallback_order": ["openai"]
        }
        
        # Load from file if exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    config.update(file_config)
                    logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                logger.error(f"Error loading config file: {e}")
        
        # Override with environment variables
        if os.getenv("OPENAI_API_KEY"):
            config["providers"]["openai"]["api_key"] = os.getenv("OPENAI_API_KEY")
        
        return config
    
    def generate_summary_simple(self, content: str) -> str:
        """Simple summary generation without complex dependencies"""
        try:
            import urllib.request
            import urllib.parse
            import json
            
            api_key = self.config["providers"]["openai"]["api_key"]
            if not api_key:
                return "Please set OPENAI_API_KEY environment variable"
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            system_prompt = "Create a concise summary (150 words max) that captures the main points."
            user_prompt = f"Please summarize the following content:\n\n{content}"
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 300,
                "temperature": 0.3
            }
            
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=data,
                headers=headers
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode('utf-8'))
                    summary = result["choices"][0]["message"]["content"].strip()
                    return summary
                else:
                    return f"Error: HTTP {response.status_code}"
        
        except Exception as e:
            logger.error(f"Summary generation error: {e}")
            return f"Error: {str(e)}"

    def _add_ai_frontmatter(self, content: str, summary: str) -> str:
        """Add AI summary to frontmatter"""
        lines = content.split('\n')
        frontmatter_end = 0
        content_start = 0
        
        # Find frontmatter boundaries
        for i, line in enumerate(lines):
            if line.strip() == '+++':
                frontmatter_end = i + 1
                break
            elif line.strip() == '---' and i > 0:
                content_start = i + 1
        
        # Build new content with AI summary
        new_content = []
        
        # Add existing frontmatter
        new_content.extend(lines[:frontmatter_end])
        
        # Check if summary already exists
        ai_summary_exists = any("ai_summary:" in line for line in lines[frontmatter_end:content_start])
        
        if not ai_summary_exists:
            # Insert AI summary fields
            new_content.extend([
                'ai_summary: f""{summary}""',
                'ai_summary_provider: "openai"',
                'ai_summary_style: "concise"',
                'ai_summary_length: len(summary.split()) if summary else 0',
                'ai_generated: true'
            ])
        
        new_content.extend(lines[frontmatter_end:])
        
        return '\n'.join(new_content)

def main():
    """Simple CLI for summary generation"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--content', type=str, help='Content to summarize')
    
    args = parser.parse_args()
    
    if not args.content:
        parser.error("Please provide content with --content")
        return
    
    generator = SummaryGenerator()
    summary = generator.generate_summary_simple(args.content)
    
    print(f"Summary: {summary}")
    
    # Write frontmatter to update file if it's a markdown file
    if args.content.endswith('.md'):
        content = generator._add_ai_frontmatter(args.content, summary)
        with open(args.content, 'w') as f:
            f.write(content)
        
        print(f"Updated: {args.content}")

if __name__ == "__main__":
    main()
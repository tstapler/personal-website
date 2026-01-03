#!/usr/bin/env python3
"""
AI Summary Generator for Hugo Blog Posts

Generic interface supporting multiple AI providers:
- OpenAI GPT models
- Local models via Ollama
- Anthropic Claude models (future)
- HuggingFace models (future)

Usage:
    python scripts/ai_summary_generator.py --content "blog post content" --provider openai
    python scripts/ai_summary_generator.py --file content/blog/post.md --provider local
"""

import asyncio
import sys
import os
import json
import logging
from pathlib import Path
from typing import Optional
from enum import Enum
from dataclasses import dataclass
try:
    from enum import Enum
except ImportError:
    # Fallback for Python < 3.4
    class Enum:
        pass
from dataclasses import dataclass
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import our provider classes
try:
    from ai_summary_providers import (
        SummaryProviderFactory, SummaryConfig, SummaryRequest, 
        ProviderType, SummaryResponse
    )
except ImportError as e:
    logger.error(f"Could not import AI providers: {e}")
    sys.exit(1)

class SummaryGenerator:
    """Main summary generation orchestrator"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = SummaryConfig(config_file)
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available providers"""
        provider_configs = self.config.get_provider_configs()
        available_providers = SummaryProviderFactory.get_available_providers(provider_configs)
        
        for provider in available_providers:
            self.providers[provider.provider_type.value] = provider
            logger.info(f"Initialized {provider.provider_type.value} provider")
    
    async def generate_summary(
        self, 
        content: str, 
        provider_name: Optional[str] = None,
        style: str = "concise",
        max_length: int = 150
    ) -> SummaryResponse:
        """Generate summary using preferred or fallback provider"""
        
        # Determine provider preference
        target_provider = provider_name or self.config.get_default_provider()
        fallback_order = self.config.get_fallback_order()
        
        # Try preferred provider first
        if target_provider in self.providers:
            logger.info(f"Trying preferred provider: {target_provider}")
            response = await self.providers[target_provider].generate_summary(
                SummaryRequest(content=content, style=style, max_length=max_length)
            )
            if response.error is None:
                return response
            logger.warning(f"Provider {target_provider} failed: {response.error}")
        
        # Try fallback providers
        for provider_name in fallback_order:
            if provider_name in self.providers and provider_name != target_provider:
                logger.info(f"Trying fallback provider: {provider_name}")
                response = await self.providers[provider_name].generate_summary(
                    SummaryRequest(content=content, style=style, max_length=max_length)
                )
                if response.error is None:
                    return response
                logger.warning(f"Fallback provider {provider_name} failed: {response.error}")
        
        # All providers failed
        return SummaryResponse(
            summary="",
            provider="none",
            model="none",
            error="All AI providers failed"
        )
    
    def get_available_providers(self) -> list:
        """Get list of available provider names"""
        return list(self.providers.keys())
    
    def get_provider_info(self) -> dict:
        """Get information about all providers"""
        info = {}
        for name, provider in self.providers.items():
            info[name] = provider.get_model_info()
        return info

async def generate_for_file(
    generator: SummaryGenerator,
    file_path: str,
    provider: Optional[str] = None
) -> Optional[str]:
    """Generate summary for a specific file"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None
    
    # Extract content after front matter for Hugo files
    if file_path.endswith('.md'):
        content = extract_hugo_content(content)
    
    response = await generator.generate_summary(
        content=content,
        provider_name=provider,
        style="concise",
        max_length=150
    )
    
    if response.error is None:
        logger.info(f"Generated summary using {response.provider}: {response.summary[:50]}...")
        return response.summary
    else:
        logger.error(f"Summary generation failed: {response.error}")
        return None

def extract_hugo_content(content: str) -> str:
    """Extract main content from Hugo markdown file"""
    lines = content.split('\n')
    content_start = 0
    
    for i, line in enumerate(lines):
        if line.strip() == '+++':
            content_start = i + 1
            break
        elif line.strip() == '---' and i > 0:
            content_start = i + 1
            break
    
    return '\n'.join(lines[content_start:]).strip()

def create_sample_config():
    """Create a sample configuration file"""
    config = {
        "providers": {
            "openai": {
                "model": "gpt-3.5-turbo",
                "api_key": "your-openai-api-key-here",
                "description": "OpenAI GPT-3.5 Turbo (fast, cost-effective)"
            },
            "anthropic": {
                "model": "claude-3-haiku-20240307",
                "api_key": "your-anthropic-api-key-here", 
                "description": "Anthropic Claude (balanced quality)"
            },
            "local": {
                "model": "llama2",
                "base_url": "http://localhost:11434",
                "timeout": 60,
                "description": "Local Ollama instance (free, private)"
            }
        },
        "default_provider": "openai",
        "fallback_order": ["local", "openai", "anthropic"],
        "cache_enabled": True,
        "cache_ttl": 3600
    }
    
    config_file = "summary_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Created sample config file: {config_file}")
    print("Edit this file to add your API keys and provider preferences.")
    return config_file

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate AI summaries for Hugo blog posts",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--content', '-c',
        type=str,
        help='Direct content to summarize'
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Markdown file to summarize'
    )
    
    parser.add_argument(
        '--provider', '-p',
        type=str,
        choices=['openai', 'local', 'anthropic'],
        help='AI provider to use (default: from config)'
    )
    
    parser.add_argument(
        '--style', '-s',
        type=str,
        choices=['concise', 'detailed', 'academic'],
        default='concise',
        help='Summary style (default: concise)'
    )
    
    parser.add_argument(
        '--max-length', '-l',
        type=int,
        default=150,
        help='Maximum summary length in words (default: 150)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Configuration file path (default: summary_config.json)'
    )
    
    parser.add_argument(
        '--create-config',
        action='store_true',
        help='Create sample configuration file and exit'
    )
    
    parser.add_argument(
        '--list-providers',
        action='store_true', 
        help='List available AI providers'
    )
    
    args = parser.parse_args()
    
    # Create config file if requested
    if args.create_config:
        create_sample_config()
        return
    
    # Initialize generator
    generator = SummaryGenerator(args.config)
    
    # List providers if requested
    if args.list_providers:
        available = generator.get_available_providers()
        info = generator.get_provider_info()
        
        print("Available AI Providers:")
        for provider_name in available:
            provider_info = info[provider_name]
            print(f"\n{provider_name.upper()}:")
            print(f"  Model: {provider_info.get('model', 'N/A')}")
            print(f"  Available: {'✓' if provider_name in available else '✗'}")
            if 'cost_per_1k_tokens' in provider_info:
                print(f"  Cost: ${provider_info['cost_per_1k_tokens']}/1K tokens")
        
        print(f"\nDefault: {generator.config.get_default_provider()}")
        print(f"Fallback order: {' → '.join(generator.config.get_fallback_order())}")
        return
    
    # Generate summary
    content = None
    source = "stdin"
    
    if args.content:
        content = args.content
        source = "command line"
    elif args.file:
        content = await generate_for_file(generator, args.file, args.provider)
        source = args.file
    else:
        # Read from stdin
        if not sys.stdin.isatty():
            content = sys.stdin.read()
            source = "stdin"
        else:
            parser.error("Please provide content via --content, --file, or stdin")
    
    if content is None:
        return
    
    # Generate the summary
    response = await generator.generate_summary(
        content=content,
        provider_name=args.provider,
        style=args.style,
        max_length=args.max_length
    )
    
    # Output results
    if response.error is None:
        print(response.summary)
        
        # Log metadata to stderr for scripts to use
        metadata = {
            "provider": response.provider,
            "model": response.model,
            "tokens_used": response.tokens_used,
            "cost": response.cost,
            "source": source
        }
        
        if response.metadata:
            metadata.update(response.metadata)
        
        print(json.dumps(metadata), file=sys.stderr)
    else:
        logger.error(f"Failed to generate summary: {response.error}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
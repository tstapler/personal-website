#!/usr/bin/env python3
"""
Simplified AI Summary Generator for Hugo Blog Posts

Generic interface supporting multiple providers:
- OpenAI via simple API calls
- Local models (future enhancement ready)
- Easy to extend with new providers

Focus on simplicity and reliability over extensive feature set.
"""

import asyncio
import sys
import os
import json
import logging
from pathlib import Path
from typing import Optional
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProviderType(Enum):
    """Supported AI provider types"""
    OPENAI = "openai"
    LOCAL = "local"

@dataclass
class SummaryRequest:
    """Request data for AI summary generation"""
    content: str
    max_length: int = 150
    style: str = "concise"  # concise, detailed, academic
    language: str = "en"
    context: Optional[str] = None
    provider: Optional[str] = None
    temperature: float = 0.3

@dataclass
class SummaryResponse:
    """Response data from AI provider"""
    summary: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    error: Optional[str] = None
    metadata: Optional[dict] = None

class SimpleOpenAIProvider:
    """Simple OpenAI provider implementation"""
    
    def __init__(self, config: dict):
        self.api_key = config.get('api_key')
        self.model = config.get('model', 'gpt-3.5-turbo')
        self.base_url = "https://api.openai.com/v1"
    
    def get_provider_type(self) -> ProviderType:
        return ProviderType.OPENAI
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def get_model_info(self) -> dict:
        return {
            "provider": "openai",
            "model": self.model,
            "max_tokens": 4096,
            "cost_per_1k_tokens": 0.002 if "3.5" in self.model else 0.01
        }
    
    async def generate_summary(self, request: SummaryRequest) -> SummaryResponse:
        """Generate summary using OpenAI API"""
        try:
            import urllib.request
            import urllib.parse
            import urllib.error
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            system_prompt = self._build_system_prompt(request.style, request.max_length)
            user_prompt = f"Please summarize the following content:\n\n{request.content}"
            
            if request.context:
                user_prompt = f"Context: {request.context}\n\n{user_prompt}"
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": min(request.max_length * 2, 1000),  # Rough estimation
                "temperature": request.temperature
            }
            
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=data,
                headers=headers
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode('utf-8'))
                    summary = result["choices"][0]["message"]["content"]
                    tokens = result.get("usage", {}).get("total_tokens", 0)
                    
                    return SummaryResponse(
                        summary=summary.strip(),
                        provider="openai",
                        model=self.model,
                        tokens_used=tokens,
                        cost=self._calculate_cost(tokens),
                        metadata={"response_time": response.headers.get("x-response-time")}
                    )
                else:
                    error_text = response.read().decode('utf-8')
                    return SummaryResponse(
                        summary="",
                        provider="openai",
                        model=self.model,
                        error=f"HTTP {response.status}: {error_text}"
                    )
        
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return SummaryResponse(
                summary="",
                provider="openai",
                model=self.model,
                error=str(e)
            )
    
    def _build_system_prompt(self, style: str, max_length: int) -> str:
        """Build system prompt based on style and length"""
        style_prompts = {
            "concise": f"Create a concise summary ({max_length} words max) that captures the main points.",
            "detailed": f"Create a detailed summary ({max_length} words max) that includes key insights and examples.",
            "academic": f"Create an academic-style summary ({max_length} words max) with proper formal tone and structure."
        }
        
        base_prompt = style_prompts.get(style, style_prompts["concise"])
        return f"""You are a professional content summarizer. {base_prompt}

Focus on:
- Main topic and key points
- Important insights or conclusions
- Technical details if relevant
- Remove filler and redundancy

Return only the summary, no additional commentary."""
    
    def _calculate_cost(self, tokens: Optional[int]) -> float:
        """Calculate cost based on token usage"""
        if not tokens:
            return 0.0
        if "3.5" in self.model:
            return (tokens / 1000) * 0.002
        elif "4" in self.model:
            return (tokens / 1000) * 0.01
        return 0.0

class SimpleLocalProvider:
    """Simple local provider placeholder"""
    
    def __init__(self, config: dict):
        self.base_url = config.get('base_url', 'http://localhost:11434')
        self.model = config.get('model', 'llama2')
    
    def get_provider_type(self) -> ProviderType:
        return ProviderType.LOCAL
    
    def is_available(self) -> bool:
        """Simple check - just check if URL responds"""
        try:
            import urllib.request
            req = urllib.request.Request(f"{self.base_url}/api/tags", timeout=5)
            with urllib.request.urlopen(req) as response:
                return response.status == 200
        except:
            return False
    
    def get_model_info(self) -> dict:
        return {
            "provider": "local",
            "model": self.model,
            "base_url": self.base_url,
            "cost_per_1k_tokens": 0.0,  # Free local inference
            "max_tokens": 4096
        }
    
    async def generate_summary(self, request: SummaryRequest) -> SummaryResponse:
        """Placeholder for local provider"""
        return SummaryResponse(
            summary="[Local provider not implemented yet - use OpenAI]",
            provider="local",
            model=self.model,
            error="Local provider not implemented"
        )

class SummaryProviderFactory:
    """Factory for creating AI providers"""
    
    @staticmethod
    def create_provider(provider_type: ProviderType, config: dict) -> object:
        """Create provider instance based on type"""
        providers = {
            ProviderType.OPENAI: SimpleOpenAIProvider,
            ProviderType.LOCAL: SimpleLocalProvider,
        }
        
        provider_class = providers.get(provider_type)
        if not provider_class:
            raise ValueError(f"Unsupported provider type: {provider_type}")
        
        return provider_class(config)
    
    @staticmethod
    def get_available_providers(configs: dict) -> list:
        """Get list of available and configured providers"""
        available = []
        
        for provider_name, config in configs.items():
            try:
                provider_type = ProviderType(provider_name)
                provider = SummaryProviderFactory.create_provider(provider_type, config)
                if provider.is_available():
                    available.append(provider)
                    logger.info(f"Provider {provider_name} is available")
                else:
                    logger.warning(f"Provider {provider_name} is configured but not available")
            except (ValueError, KeyError) as e:
                logger.error(f"Invalid provider configuration {provider_name}: {e}")
        
        return available

class SummaryConfig:
    """Manage configuration for AI providers"""
    
    DEFAULT_CONFIG = {
        "providers": {
            "openai": {
                "model": "gpt-3.5-turbo",
                "api_key": None  # Set via environment variable
            },
            "local": {
                "model": "llama2",
                "base_url": "http://localhost:11434",
                "timeout": 60
            }
        },
        "default_provider": "openai",
        "fallback_order": ["openai", "local"],
        "cache_enabled": True,
        "cache_ttl": 3600  # 1 hour
    }
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "summary_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from file and environment"""
        config = self.DEFAULT_CONFIG.copy()
        
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
    
    def get_provider_configs(self) -> dict:
        """Get all provider configurations"""
        return self.config["providers"]
    
    def get_default_provider(self) -> str:
        """Get default provider name"""
        return self.config["default_provider"]
    
    def get_fallback_order(self) -> list:
        """Get fallback provider order"""
        return self.config["fallback_order"]

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
            self.providers[provider.get_provider_type().value] = provider
            logger.info(f"Initialized {provider.get_provider_type().value} provider")
    
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
            "local": {
                "model": "llama2",
                "base_url": "http://localhost:11434",
                "timeout": 60,
                "description": "Local Ollama instance (free, private)"
            }
        },
        "default_provider": "openai",
        "fallback_order": ["openai", "local"],
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
        choices=['openai', 'local'],
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
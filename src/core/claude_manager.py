#!/usr/bin/env python3
"""
Claude Model Manager
Automatically detects and uses the latest available Claude model
"""

import os
import anthropic
import logging
from typing import Optional, List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class ClaudeModelManager:
    """Manages Claude model selection and provides latest model detection"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.client = None
        self._latest_model = None
        self._model_cache = {}
        self._cache_expiry = None
        self._cache_duration = 3600  # 1 hour cache
        
        if self.api_key:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info("✅ Claude Model Manager initialized with API key")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Claude client: {e}")
                self.client = None
        else:
            logger.warning("⚠️ No ANTHROPIC_API_KEY found")
    
    def get_available_models(self) -> List[Dict[str, str]]:
        """Get list of available models with metadata"""
        if not self.client:
            logger.error("❌ Claude client not initialized")
            return []
        
        try:
            models_response = self.client.models.list()
            models = []
            
            for model in models_response.data:
                model_info = {
                    'id': model.id,
                    'name': model.id,
                    'type': self._get_model_type(model.id),
                    'version': self._get_model_version(model.id),
                    'date': self._get_model_date(model.id)
                }
                models.append(model_info)
            
            # Sort by type priority and date (newest first)
            models.sort(key=lambda x: (
                self._get_type_priority(x['type']),
                x['date']
            ), reverse=True)
            
            logger.info(f"📋 Found {len(models)} available Claude models")
            return models
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch available models: {e}")
            return []
    
    def get_latest_model(self, preferred_type: str = "sonnet") -> Optional[str]:
        """
        Get the latest available model of preferred type
        
        Args:
            preferred_type: Preferred model type (sonnet, opus, haiku)
        
        Returns:
            Model ID of the latest model, or None if not found
        """
        # Check cache first (but only for the same preferred type)
        cache_key = f"{preferred_type}_{self._latest_model}"
        if (self._latest_model and 
            self._cache_expiry and 
            datetime.now().timestamp() < self._cache_expiry and
            hasattr(self, '_cached_type') and
            self._cached_type == preferred_type):
            logger.debug(f"🔄 Using cached latest {preferred_type} model: {self._latest_model}")
            return self._latest_model
        
        models = self.get_available_models()
        if not models:
            logger.error("❌ No models available")
            return None
        
        # Find latest model of preferred type
        preferred_models = [m for m in models if m['type'] == preferred_type]
        if preferred_models:
            latest_model = preferred_models[0]['id']
            logger.info(f"🎯 Latest {preferred_type} model: {latest_model}")
        else:
            # Fallback to any latest model
            latest_model = models[0]['id']
            logger.info(f"🎯 No {preferred_type} model found, using latest available: {latest_model}")
        
        # Cache the result
        self._latest_model = latest_model
        self._cached_type = preferred_type
        self._cache_expiry = datetime.now().timestamp() + self._cache_duration
        
        return latest_model
    
    def get_model_info(self, model_id: str) -> Dict[str, str]:
        """Get detailed information about a specific model"""
        models = self.get_available_models()
        for model in models:
            if model['id'] == model_id:
                return model
        return {}
    
    def _get_model_type(self, model_id: str) -> str:
        """Extract model type from model ID"""
        if 'opus' in model_id.lower():
            return 'opus'
        elif 'sonnet' in model_id.lower():
            return 'sonnet'
        elif 'haiku' in model_id.lower():
            return 'haiku'
        else:
            return 'unknown'
    
    def _get_model_version(self, model_id: str) -> str:
        """Extract version from model ID"""
        parts = model_id.split('-')
        if len(parts) >= 3:
            return f"{parts[1]}-{parts[2]}"
        return "unknown"
    
    def _get_model_date(self, model_id: str) -> str:
        """Extract date from model ID"""
        parts = model_id.split('-')
        if len(parts) >= 4:
            return parts[-1]
        return "unknown"
    
    def _get_type_priority(self, model_type: str) -> int:
        """Get priority for model type (higher = better)"""
        priorities = {
            'opus': 3,
            'sonnet': 2,
            'haiku': 1,
            'unknown': 0
        }
        return priorities.get(model_type, 0)
    
    def is_model_available(self, model_id: str) -> bool:
        """Check if a specific model is available"""
        models = self.get_available_models()
        return any(model['id'] == model_id for model in models)
    
    def get_recommended_model(self) -> str:
        """
        Get the recommended model based on availability and performance
        
        Priority:
        1. Latest Sonnet (best balance of performance/cost)
        2. Latest Opus (highest performance)
        3. Latest Haiku (fastest/cheapest)
        """
        # Try to get latest Sonnet first
        latest_sonnet = self.get_latest_model('sonnet')
        if latest_sonnet:
            logger.info(f"🎯 Recommended model (Sonnet): {latest_sonnet}")
            return latest_sonnet
        
        # Fallback to latest Opus
        latest_opus = self.get_latest_model('opus')
        if latest_opus:
            logger.info(f"🎯 Recommended model (Opus): {latest_opus}")
            return latest_opus
        
        # Fallback to latest Haiku
        latest_haiku = self.get_latest_model('haiku')
        if latest_haiku:
            logger.info(f"🎯 Recommended model (Haiku): {latest_haiku}")
            return latest_haiku
        
        # Last resort - any available model
        models = self.get_available_models()
        if models:
            fallback_model = models[0]['id']
            logger.warning(f"⚠️ Using fallback model: {fallback_model}")
            return fallback_model
        
        logger.error("❌ No models available")
        return "claude-3-haiku-20240307"  # Hardcoded fallback

def test_model_manager():
    """Test the Claude Model Manager"""
    print("🤖 Testing Claude Model Manager")
    print("=" * 50)
    
    manager = ClaudeModelManager()
    
    if not manager.client:
        print("❌ Claude client not initialized - check API key")
        return False
    
    # Test getting available models
    print("📋 Available models:")
    models = manager.get_available_models()
    for i, model in enumerate(models[:5]):  # Show first 5
        print(f"  {i+1}. {model['id']} ({model['type']})")
    
    # Test getting latest model
    print(f"\n🎯 Latest Sonnet model: {manager.get_latest_model('sonnet')}")
    print(f"🎯 Latest Opus model: {manager.get_latest_model('opus')}")
    print(f"🎯 Latest Haiku model: {manager.get_latest_model('haiku')}")
    
    # Test recommended model
    recommended = manager.get_recommended_model()
    print(f"\n✅ Recommended model: {recommended}")
    
    return True

if __name__ == "__main__":
    test_model_manager()

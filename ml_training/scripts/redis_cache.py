#!/usr/bin/env python3
"""
Sisi Lola Redis Caching Layer
Provides distributed caching for:
1. Response caching - cache generated responses
2. Embedding caching - cache computed embeddings
3. Session state - maintain conversation context

Falls back to in-memory cache if Redis unavailable.
"""
import os
import sys
import json
import hashlib
import pickle
from pathlib import Path
from typing import Optional, Any, Dict, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import yaml

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class CacheConfig:
    """Redis cache configuration"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    response_ttl: int = 3600  # 1 hour
    embedding_ttl: int = 86400  # 24 hours
    session_ttl: int = 1800  # 30 minutes
    max_memory_entries: int = 10000


class InMemoryCache:
    """
    Fallback in-memory cache when Redis is unavailable.
    Uses LRU-style eviction.
    """
    
    def __init__(self, max_entries: int = 10000):
        self._cache: Dict[str, tuple] = {}  # key -> (value, expiry, access_time)
        self._max_entries = max_entries
    
    def _evict_if_needed(self):
        """Evict oldest entries if over capacity"""
        while len(self._cache) >= self._max_entries:
            # Find oldest entry
            oldest_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k][2]  # access_time
            )
            del self._cache[oldest_key]
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self._cache:
            return None
        
        value, expiry, _ = self._cache[key]
        
        # Check expiry
        if expiry and datetime.now() > expiry:
            del self._cache[key]
            return None
        
        # Update access time
        self._cache[key] = (value, expiry, datetime.now())
        return value
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """Set value in cache"""
        self._evict_if_needed()
        expiry = datetime.now() + timedelta(seconds=ttl_seconds)
        self._cache[key] = (value, expiry, datetime.now())
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self):
        """Clear all cache entries"""
        self._cache.clear()
    
    def size(self) -> int:
        """Get number of entries"""
        return len(self._cache)


class RedisCache:
    """
    Redis-backed cache with fallback to in-memory.
    
    Features:
    - Automatic serialization/deserialization
    - TTL support
    - Namespace prefixing
    - Connection pooling
    - Graceful fallback
    """
    
    def __init__(self, config: Optional[CacheConfig] = None, namespace: str = "sisilola"):
        self.config = config or self._load_config()
        self.namespace = namespace
        self._redis = None
        self._fallback = InMemoryCache(self.config.max_memory_entries)
        self._using_fallback = False
        
        self._connect()
    
    def _load_config(self) -> CacheConfig:
        """Load cache config from optimization config"""
        config_path = PROJECT_ROOT / "ml_training" / "configs" / "optimization_config.yaml"
        
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
                caching = config.get('caching', {})
                redis_cfg = caching.get('redis', {})
                
                return CacheConfig(
                    host=redis_cfg.get('host', 'localhost'),
                    port=redis_cfg.get('port', 6379),
                    db=redis_cfg.get('db', 0),
                    password=redis_cfg.get('password'),
                    response_ttl=caching.get('response_cache', {}).get('ttl_seconds', 3600),
                    embedding_ttl=caching.get('embedding_cache', {}).get('ttl_seconds', 86400)
                )
        
        return CacheConfig()
    
    def _connect(self):
        """Connect to Redis"""
        try:
            import redis
            self._redis = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                decode_responses=False,  # We handle serialization
                socket_connect_timeout=5
            )
            # Test connection
            self._redis.ping()
            print(f"✅ Connected to Redis at {self.config.host}:{self.config.port}")
            self._using_fallback = False
            
        except Exception as e:
            print(f"⚠️ Redis unavailable ({e}), using in-memory cache")
            self._redis = None
            self._using_fallback = True
    
    def _make_key(self, key: str) -> str:
        """Create namespaced key"""
        return f"{self.namespace}:{key}"
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage"""
        try:
            return json.dumps(value).encode('utf-8')
        except (TypeError, ValueError):
            return pickle.dumps(value)
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from storage"""
        try:
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return pickle.loads(data)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        full_key = self._make_key(key)
        
        if self._using_fallback:
            return self._fallback.get(full_key)
        
        try:
            data = self._redis.get(full_key)
            if data is None:
                return None
            return self._deserialize(data)
        except Exception as e:
            print(f"⚠️ Redis get error: {e}")
            return self._fallback.get(full_key)
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time-to-live in seconds
        """
        full_key = self._make_key(key)
        ttl = ttl_seconds or self.config.response_ttl
        
        if self._using_fallback:
            self._fallback.set(full_key, value, ttl)
            return
        
        try:
            data = self._serialize(value)
            self._redis.setex(full_key, ttl, data)
        except Exception as e:
            print(f"⚠️ Redis set error: {e}")
            self._fallback.set(full_key, value, ttl)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        full_key = self._make_key(key)
        
        if self._using_fallback:
            return self._fallback.delete(full_key)
        
        try:
            return self._redis.delete(full_key) > 0
        except Exception as e:
            print(f"⚠️ Redis delete error: {e}")
            return self._fallback.delete(full_key)
    
    def clear_namespace(self):
        """Clear all keys in namespace"""
        if self._using_fallback:
            self._fallback.clear()
            return
        
        try:
            pattern = f"{self.namespace}:*"
            keys = self._redis.keys(pattern)
            if keys:
                self._redis.delete(*keys)
        except Exception as e:
            print(f"⚠️ Redis clear error: {e}")
            self._fallback.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            "using_fallback": self._using_fallback,
            "namespace": self.namespace,
            "config": {
                "host": self.config.host,
                "port": self.config.port,
                "response_ttl": self.config.response_ttl
            }
        }
        
        if self._using_fallback:
            stats["entries"] = self._fallback.size()
        else:
            try:
                info = self._redis.info('memory')
                stats["redis_memory_mb"] = info.get('used_memory', 0) / 1024 / 1024
                stats["entries"] = self._redis.dbsize()
            except:
                pass
        
        return stats


class ResponseCache:
    """
    Specialized cache for LLM responses.
    
    Features:
    - Prompt hashing for cache keys
    - Config-aware caching (different responses for different params)
    - Hit rate tracking
    """
    
    def __init__(self, redis_cache: Optional[RedisCache] = None):
        self._cache = redis_cache or RedisCache(namespace="sisilola:responses")
        self._hits = 0
        self._misses = 0
    
    def _make_key(self, prompt: str, config: Dict = None) -> str:
        """Create cache key from prompt and config"""
        config_str = json.dumps(config or {}, sort_keys=True)
        key_data = f"{prompt}|{config_str}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:32]
    
    def get(self, prompt: str, config: Dict = None) -> Optional[str]:
        """Get cached response"""
        key = self._make_key(prompt, config)
        result = self._cache.get(key)
        
        if result is not None:
            self._hits += 1
        else:
            self._misses += 1
        
        return result
    
    def set(self, prompt: str, response: str, config: Dict = None, ttl: int = None):
        """Cache a response"""
        key = self._make_key(prompt, config)
        self._cache.set(key, response, ttl)
    
    def invalidate(self, prompt: str, config: Dict = None):
        """Invalidate a cached response"""
        key = self._make_key(prompt, config)
        self._cache.delete(key)
    
    @property
    def hit_rate(self) -> float:
        """Get cache hit rate"""
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{self.hit_rate:.1%}",
            "backend": self._cache.get_stats()
        }


class EmbeddingCache:
    """
    Specialized cache for embeddings.
    
    Used for:
    - Speaker embeddings (voice cloning)
    - Text embeddings (semantic search)
    """
    
    def __init__(self, redis_cache: Optional[RedisCache] = None):
        self._cache = redis_cache or RedisCache(namespace="sisilola:embeddings")
    
    def _make_key(self, text: str, model: str = "default") -> str:
        """Create cache key"""
        key_data = f"{model}|{text}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:32]
    
    def get(self, text: str, model: str = "default") -> Optional[list]:
        """Get cached embedding"""
        key = self._make_key(text, model)
        return self._cache.get(key)
    
    def set(self, text: str, embedding: list, model: str = "default", ttl: int = 86400):
        """Cache an embedding"""
        key = self._make_key(text, model)
        self._cache.set(key, embedding, ttl)


class SessionCache:
    """
    Cache for conversation sessions.
    
    Maintains:
    - Conversation history
    - User context
    - Session state
    """
    
    def __init__(self, redis_cache: Optional[RedisCache] = None):
        self._cache = redis_cache or RedisCache(namespace="sisilola:sessions")
        self._default_ttl = 1800  # 30 minutes
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        return self._cache.get(session_id)
    
    def update_session(self, session_id: str, data: Dict, extend_ttl: bool = True):
        """Update session data"""
        existing = self.get_session(session_id) or {}
        existing.update(data)
        self._cache.set(session_id, existing, self._default_ttl if extend_ttl else None)
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add message to session history"""
        session = self.get_session(session_id) or {"history": []}
        
        if "history" not in session:
            session["history"] = []
        
        session["history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep last 20 messages
        session["history"] = session["history"][-20:]
        
        self._cache.set(session_id, session, self._default_ttl)
    
    def get_history(self, session_id: str, limit: int = 10) -> list:
        """Get conversation history"""
        session = self.get_session(session_id)
        if session and "history" in session:
            return session["history"][-limit:]
        return []
    
    def clear_session(self, session_id: str):
        """Clear session data"""
        self._cache.delete(session_id)


# Singleton instances
_response_cache: Optional[ResponseCache] = None
_embedding_cache: Optional[EmbeddingCache] = None
_session_cache: Optional[SessionCache] = None


def get_response_cache() -> ResponseCache:
    """Get global response cache"""
    global _response_cache
    if _response_cache is None:
        _response_cache = ResponseCache()
    return _response_cache


def get_embedding_cache() -> EmbeddingCache:
    """Get global embedding cache"""
    global _embedding_cache
    if _embedding_cache is None:
        _embedding_cache = EmbeddingCache()
    return _embedding_cache


def get_session_cache() -> SessionCache:
    """Get global session cache"""
    global _session_cache
    if _session_cache is None:
        _session_cache = SessionCache()
    return _session_cache


def main():
    """Demo caching functionality"""
    print("="*60)
    print("Caching Layer Demo")
    print("="*60)
    
    # Response cache demo
    print("\n📦 Response Cache:")
    cache = get_response_cache()
    
    # Test caching
    prompt = "Hello, how are you?"
    config = {"temperature": 0.8}
    
    # Miss
    result = cache.get(prompt, config)
    print(f"   First request (miss): {result}")
    
    # Set
    cache.set(prompt, "E kaa san! I dey fine!", config)
    print("   Cached response")
    
    # Hit
    result = cache.get(prompt, config)
    print(f"   Second request (hit): {result}")
    
    print(f"\n   Stats: {cache.get_stats()}")
    
    # Session cache demo
    print("\n💬 Session Cache:")
    sessions = get_session_cache()
    
    session_id = "demo_session_123"
    sessions.add_message(session_id, "user", "Hello!")
    sessions.add_message(session_id, "assistant", "E ku aro! How you dey?")
    
    history = sessions.get_history(session_id)
    print(f"   Session history: {len(history)} messages")
    for msg in history:
        print(f"      [{msg['role']}]: {msg['content'][:30]}...")
    
    print("\n✅ Caching layer demo complete!")


if __name__ == "__main__":
    main()

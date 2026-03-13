"""
Unit tests for CacheManager
Tests all caching functionalities
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from datetime import datetime, timedelta
import json
from src.core.cache import CacheManager, cache_manager, cache_veille_data, cached


class TestCacheManager:
    """Test CacheManager class"""
    
    @pytest.fixture
    def cache(self):
        """Create a CacheManager instance"""
        return CacheManager()
    
    @pytest.mark.asyncio
    async def test_cache_initialization(self, cache):
        """Test cache initialization"""
        assert hasattr(cache, '_cache')
        assert hasattr(cache, '_ttl')
        assert hasattr(cache, '_lock')
    
    @pytest.mark.asyncio
    async def test_set_and_get(self, cache):
        """Test basic set and get operations"""
        # Set value
        await cache.set("test_key", "test_value")
        
        # Get value
        value = await cache.get("test_key")
        assert value == "test_value"
    
    @pytest.mark.asyncio
    async def test_set_with_ttl(self, cache):
        """Test set with custom TTL"""
        # Set value with short TTL
        await cache.set("test_key", "test_value", ttl=1)
        
        # Get value immediately
        value = await cache.get("test_key")
        assert value == "test_value"
        
        # Wait for expiration
        await asyncio.sleep(1.1)
        
        # Value should be expired
        value = await cache.get("test_key")
        assert value is None
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, cache):
        """Test getting non-existent key"""
        value = await cache.get("nonexistent_key")
        assert value is None
    
    @pytest.mark.asyncio
    async def test_delete(self, cache):
        """Test delete operation"""
        # Set value
        await cache.set("test_key", "test_value")
        
        # Verify it exists
        value = await cache.get("test_key")
        assert value == "test_value"
        
        # Delete it
        result = await cache.delete("test_key")
        assert result is True
        
        # Verify it's gone
        value = await cache.get("test_key")
        assert value is None
    
    @pytest.mark.asyncio
    async def test_clear(self, cache):
        """Test clear operation"""
        # Set multiple values
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")
        
        # Verify they exist
        assert await cache.get("key1") == "value1"
        assert await cache.get("key2") == "value2"
        assert await cache.get("key3") == "value3"
        
        # Clear cache
        count = await cache.clear()
        assert count == 3
        
        # Verify all are gone
        assert await cache.get("key1") is None
        assert await cache.get("key2") is None
        assert await cache.get("key3") is None
    
    @pytest.mark.asyncio
    async def test_complex_data_types(self, cache):
        """Test caching complex data types"""
        # Test dictionary
        test_dict = {"key": "value", "number": 42, "list": [1, 2, 3]}
        await cache.set("dict_key", test_dict)
        retrieved_dict = await cache.get("dict_key")
        assert retrieved_dict == test_dict
        
        # Test list
        test_list = [1, "string", {"nested": "value"}]
        await cache.set("list_key", test_list)
        retrieved_list = await cache.get("list_key")
        assert retrieved_list == test_list
        
        # Test datetime
        test_datetime = datetime.now()
        await cache.set("datetime_key", test_datetime)
        retrieved_datetime = await cache.get("datetime_key")
        assert retrieved_datetime == test_datetime
    
    @pytest.mark.asyncio
    async def test_concurrent_access(self, cache):
        """Test concurrent cache access"""
        async def set_value(key, value):
            await cache.set(key, value)
            return await cache.get(key)
        
        # Run multiple concurrent operations
        tasks = [
            set_value(f"key_{i}", f"value_{i}")
            for i in range(10)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Verify all operations completed successfully
        for i, result in enumerate(results):
            assert result == f"value_{i}"
    
    @pytest.mark.asyncio
    async def test_ttl_expiration(self, cache):
        """Test TTL expiration mechanism"""
        # Set value with very short TTL
        await cache.set("expire_key", "expire_value", ttl=0.1)
        
        # Value should exist immediately
        value = await cache.get("expire_key")
        assert value == "expire_value"
        
        # Wait for expiration
        await asyncio.sleep(0.2)
        
        # Value should be expired
        value = await cache.get("expire_key")
        assert value is None


class TestCacheManagerInstance:
    """Test the global cache_manager instance"""
    
    @pytest.mark.asyncio
    async def test_global_instance(self):
        """Test the global cache_manager instance"""
        # Test basic operations
        await cache_manager.set("global_key", "global_value")
        value = await cache_manager.get("global_key")
        assert value == "global_value"
        
        # Test clear
        count = await cache_manager.clear()
        assert count >= 1
        value = await cache_manager.get("global_key")
        assert value is None


class TestCacheVeilleData:
    """Test cache_veille_data function"""
    
    @pytest.mark.asyncio
    async def test_cache_veille_data(self):
        """Test caching veille data"""
        competitors = ["microsoft", "google"]
        date = "2025-01-15"
        
        # Cache veille data
        data = await cache_veille_data(competitors, date)
        
        # Verify it was cached
        key = f"veille_{date}_{'_'.join(competitors)}"
        cached_data = await cache_manager.get(key)
        assert cached_data is not None
        assert cached_data["competitors"] == competitors
        assert cached_data["date"] == date
        
        # Clean up
        await cache_manager.delete(key)


class TestCachedDecorator:
    """Test the cached decorator"""
    
    @pytest.mark.asyncio
    async def test_cached_decorator(self):
        """Test the cached decorator"""
        call_count = 0
        
        @cached(ttl=60)
        async def test_function(param):
            nonlocal call_count
            call_count += 1
            return f"result_{param}"
        
        # First call should execute function
        result1 = await test_function("test")
        assert result1 == "result_test"
        assert call_count == 1
        
        # Second call with same parameters should use cache
        result2 = await test_function("test")
        assert result2 == "result_test"
        assert call_count == 1  # Should not increment
        
        # Different parameters should execute function again
        result3 = await test_function("different")
        assert result3 == "result_different"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_cached_decorator_with_complex_params(self):
        """Test cached decorator with complex parameters"""
        call_count = 0
        
        @cached(ttl=60)
        async def test_function(param1, param2, **kwargs):
            nonlocal call_count
            call_count += 1
            return f"result_{param1}_{param2}_{kwargs.get('extra', '')}"
        
        # Test with complex parameters
        result1 = await test_function("a", "b", extra="test")
        assert result1 == "result_a_b_test"
        assert call_count == 1
        
        # Same parameters should use cache
        result2 = await test_function("a", "b", extra="test")
        assert result2 == "result_a_b_test"
        assert call_count == 1
        
        # Different parameters should execute again
        result3 = await test_function("a", "b", extra="different")
        assert result3 == "result_a_b_different"
        assert call_count == 2


class TestCacheManagerIntegration:
    """Integration tests for CacheManager"""
    
    @pytest.mark.asyncio
    async def test_cache_manager_integration(self):
        """Test complete cache manager workflow"""
        cache = CacheManager()
        
        # 1. Set multiple values
        await cache.set("key1", "value1", ttl=60)
        await cache.set("key2", "value2", ttl=120)
        await cache.set("key3", "value3", ttl=180)
        
        # 2. Verify all values exist
        assert await cache.get("key1") == "value1"
        assert await cache.get("key2") == "value2"
        assert await cache.get("key3") == "value3"
        
        # 3. Update a value
        await cache.set("key1", "updated_value1")
        assert await cache.get("key1") == "updated_value1"
        
        # 4. Delete a value
        result = await cache.delete("key2")
        assert result is True
        assert await cache.get("key2") is None
        
        # 5. Clear cache
        count = await cache.clear()
        assert count >= 2
        assert await cache.get("key1") is None
        assert await cache.get("key3") is None
    
    @pytest.mark.asyncio
    async def test_cache_with_veille_data_integration(self):
        """Test cache integration with veille data"""
        # 1. Cache veille data
        competitors = ["microsoft", "google"]
        date = "2025-01-15"
        
        data = await cache_veille_data(competitors, date)
        
        # 2. Verify data is cached
        key = f"veille_{date}_{'_'.join(competitors)}"
        cached_data = await cache_manager.get(key)
        assert cached_data is not None
        assert cached_data["competitors"] == competitors
        
        # 3. Use cached decorator
        @cached(ttl=1800)
        async def process_veille_data(comp_list, date_str):
            return {"processed": True, "count": len(comp_list)}
        
        result = await process_veille_data(competitors, date)
        assert result["processed"] is True
        assert result["count"] == 2
        
        # 4. Clean up
        await cache_manager.delete(key) 
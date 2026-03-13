"""
Smoke tests for data store functionality
Tests basic CRUD operations for competitors and posts
"""

import pytest
from datetime import datetime, timedelta
from typing import List
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.schema.post import Post, Competitor, PlatformType


class MockStore:
    """Mock store implementation for testing"""
    
    def __init__(self):
        self.competitors = {}
        self.posts = {}
        self.next_id = 1
    
    def create_competitor(self, competitor: Competitor) -> int:
        """Create a new competitor"""
        competitor_id = self.next_id
        self.next_id += 1
        competitor.id = competitor_id
        competitor.created_at = datetime.now()
        self.competitors[competitor_id] = competitor
        return competitor_id
    
    def get_competitor(self, competitor_id: int) -> Competitor:
        """Get competitor by ID"""
        return self.competitors.get(competitor_id)
    
    def list_competitors(self) -> List[Competitor]:
        """List all competitors"""
        return list(self.competitors.values())
    
    def update_competitor(self, competitor_id: int, updates: dict) -> bool:
        """Update competitor"""
        if competitor_id in self.competitors:
            for key, value in updates.items():
                setattr(self.competitors[competitor_id], key, value)
            return True
        return False
    
    def delete_competitor(self, competitor_id: int) -> bool:
        """Delete competitor"""
        if competitor_id in self.competitors:
            del self.competitors[competitor_id]
            return True
        return False
    
    def create_post(self, post: Post) -> str:
        """Create a new post"""
        post_id = f"post_{self.next_id}"
        self.next_id += 1
        post.scraped_at = datetime.now()
        self.posts[post_id] = post
        return post_id
    
    def get_posts(self, competitor_id: int = None, limit: int = 50) -> List[Post]:
        """Get posts, optionally filtered by competitor"""
        posts = list(self.posts.values())
        
        if competitor_id:
            # Filter by competitor account name (simplified for mock)
            competitor = self.get_competitor(competitor_id)
            if competitor:
                posts = [p for p in posts if p.account == competitor.handle]
        
        # Sort by posted_at descending
        posts.sort(key=lambda x: x.posted_at or datetime.min, reverse=True)
        return posts[:limit]
    
    def get_posts_since(self, since: str, competitor_id: int = None) -> List[Post]:
        """Get posts since a time period"""
        # Parse since parameter (simplified)
        days_map = {"1d": 1, "7d": 7, "30d": 30, "90d": 90}
        days = days_map.get(since, 7)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        posts = self.get_posts(competitor_id)
        return [p for p in posts if p.posted_at and p.posted_at >= cutoff_date]


class TestStoreSmoke:
    """Smoke tests for data store operations"""
    
    def setup_method(self):
        """Set up test data"""
        self.store = MockStore()
    
    def test_create_competitor(self):
        """Test creating a competitor"""
        competitor = Competitor(
            name="Nike",
            platform=PlatformType.INSTAGRAM,
            handle="nike",
            description="Athletic wear company",
            industry="sportswear"
        )
        
        competitor_id = self.store.create_competitor(competitor)
        assert competitor_id == 1
        assert competitor.id == 1
        assert competitor.created_at is not None
    
    def test_get_competitor(self):
        """Test retrieving a competitor"""
        competitor = Competitor(
            name="Adidas",
            platform=PlatformType.INSTAGRAM,
            handle="adidas"
        )
        
        competitor_id = self.store.create_competitor(competitor)
        retrieved = self.store.get_competitor(competitor_id)
        
        assert retrieved is not None
        assert retrieved.name == "Adidas"
        assert retrieved.handle == "adidas"
        assert retrieved.platform == PlatformType.INSTAGRAM
    
    def test_list_competitors(self):
        """Test listing all competitors"""
        # Create multiple competitors
        competitors_data = [
            {"name": "Nike", "platform": "instagram", "handle": "nike"},
            {"name": "Adidas", "platform": "instagram", "handle": "adidas"},
            {"name": "Puma", "platform": "linkedin", "handle": "puma"}
        ]
        
        for data in competitors_data:
            competitor = Competitor(**data)
            self.store.create_competitor(competitor)
        
        all_competitors = self.store.list_competitors()
        assert len(all_competitors) == 3
        
        names = [c.name for c in all_competitors]
        assert "Nike" in names
        assert "Adidas" in names
        assert "Puma" in names
    
    def test_update_competitor(self):
        """Test updating a competitor"""
        competitor = Competitor(
            name="Test Brand",
            platform=PlatformType.INSTAGRAM,
            handle="testbrand"
        )
        
        competitor_id = self.store.create_competitor(competitor)
        
        # Update competitor
        success = self.store.update_competitor(competitor_id, {
            "description": "Updated description",
            "follower_count": 100000
        })
        
        assert success is True
        
        updated = self.store.get_competitor(competitor_id)
        assert updated.description == "Updated description"
        assert updated.follower_count == 100000
    
    def test_delete_competitor(self):
        """Test deleting a competitor"""
        competitor = Competitor(
            name="To Delete",
            platform=PlatformType.INSTAGRAM,
            handle="todelete"
        )
        
        competitor_id = self.store.create_competitor(competitor)
        assert self.store.get_competitor(competitor_id) is not None
        
        # Delete competitor
        success = self.store.delete_competitor(competitor_id)
        assert success is True
        
        # Verify deletion
        deleted = self.store.get_competitor(competitor_id)
        assert deleted is None
    
    def test_create_post(self):
        """Test creating a post"""
        post = Post(
            platform=PlatformType.INSTAGRAM,
            account="nike",
            url="https://instagram.com/p/test123",
            posted_at=datetime.now(),
            text="Test post #nike #sports",
            likes=1500,
            comments=25,
            hashtags=["nike", "sports"]
        )
        
        post_id = self.store.create_post(post)
        assert post_id == "post_1"
        assert post.scraped_at is not None
    
    def test_get_posts_basic(self):
        """Test getting posts without filters"""
        # Create sample posts
        posts_data = [
            {
                "platform": "instagram",
                "account": "nike",
                "text": "Nike post 1",
                "likes": 1000,
                "posted_at": datetime.now() - timedelta(hours=1)
            },
            {
                "platform": "instagram", 
                "account": "adidas",
                "text": "Adidas post 1",
                "likes": 800,
                "posted_at": datetime.now() - timedelta(hours=2)
            }
        ]
        
        for data in posts_data:
            post = Post(**data)
            self.store.create_post(post)
        
        posts = self.store.get_posts()
        assert len(posts) == 2
        
        # Should be sorted by posted_at descending
        assert posts[0].account == "nike"  # More recent
        assert posts[1].account == "adidas"
    
    def test_get_posts_with_competitor_filter(self):
        """Test getting posts filtered by competitor"""
        # Create competitor
        nike_competitor = Competitor(
            name="Nike",
            platform=PlatformType.INSTAGRAM,
            handle="nike"
        )
        nike_id = self.store.create_competitor(nike_competitor)
        
        # Create posts for different accounts
        posts_data = [
            {"platform": "instagram", "account": "nike", "text": "Nike post"},
            {"platform": "instagram", "account": "adidas", "text": "Adidas post"},
            {"platform": "instagram", "account": "nike", "text": "Another Nike post"}
        ]
        
        for data in posts_data:
            post = Post(**data)
            self.store.create_post(post)
        
        # Get posts for Nike only
        nike_posts = self.store.get_posts(competitor_id=nike_id)
        assert len(nike_posts) == 2
        assert all(post.account == "nike" for post in nike_posts)
    
    def test_get_posts_since_time_filter(self):
        """Test getting posts with time-based filtering"""
        # Create posts with different timestamps
        old_post = Post(
            platform=PlatformType.INSTAGRAM,
            account="nike",
            text="Old post",
            posted_at=datetime.now() - timedelta(days=10)
        )
        
        recent_post = Post(
            platform=PlatformType.INSTAGRAM,
            account="nike",
            text="Recent post",
            posted_at=datetime.now() - timedelta(hours=1)
        )
        
        self.store.create_post(old_post)
        self.store.create_post(recent_post)
        
        # Get posts from last 7 days
        recent_posts = self.store.get_posts_since("7d")
        assert len(recent_posts) == 1
        assert recent_posts[0].text == "Recent post"
        
        # Get posts from last 30 days
        all_posts = self.store.get_posts_since("30d")
        assert len(all_posts) == 2
    
    def test_store_pagination_limit(self):
        """Test store respects limit parameter"""
        # Create many posts
        for i in range(20):
            post = Post(
                platform=PlatformType.INSTAGRAM,
                account="test",
                text=f"Post {i}",
                posted_at=datetime.now() - timedelta(minutes=i)
            )
            self.store.create_post(post)
        
        # Test limit
        limited_posts = self.store.get_posts(limit=5)
        assert len(limited_posts) == 5
        
        # Test default limit
        default_posts = self.store.get_posts()
        assert len(default_posts) <= 50  # Default limit


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
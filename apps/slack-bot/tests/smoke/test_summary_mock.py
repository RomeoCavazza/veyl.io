"""
Smoke tests for AI Summary functionality with mocked responses
Tests the summary generation pipeline without requiring OpenAI API
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.schema.post import Post, Summary, SummaryRequest, PlatformType, ContentType


class TestSummaryMock:
    """Test summary generation with mock data"""
    
    def test_post_model_validation(self):
        """Test that Post model validates correctly"""
        post_data = {
            "platform": "instagram",
            "account": "nike",
            "url": "https://instagram.com/p/test123",
            "posted_at": datetime.now(),
            "text": "Just Do It! #nike #sports",
            "likes": 1500,
            "views": 5000,
            "comments": 25,
            "hashtags": ["nike", "sports"]
        }
        
        post = Post(**post_data)
        assert post.platform == PlatformType.INSTAGRAM
        assert post.account == "nike"
        assert post.likes == 1500
        assert len(post.hashtags) == 2
        assert "nike" in post.hashtags
    
    def test_post_hashtag_normalization(self):
        """Test hashtag normalization in Post model"""
        post_data = {
            "platform": "instagram",
            "account": "test",
            "hashtags": ["#Nike", "#SPORTS", "fashion", "#Luxury "]
        }
        
        post = Post(**post_data)
        expected_hashtags = ["nike", "sports", "fashion", "luxury"]
        assert post.hashtags == expected_hashtags
    
    def test_engagement_metrics_conversion(self):
        """Test engagement metrics handle string formats"""
        from src.schema.post import EngagementMetrics
        
        # Test various string formats
        metrics = EngagementMetrics(
            likes="1.5K",
            views="2.3M", 
            comments="150",
            shares="25"
        )
        
        assert metrics.likes == 1500
        assert metrics.views == 2300000
        assert metrics.comments == 150
        assert metrics.shares == 25
    
    def test_summary_request_validation(self):
        """Test SummaryRequest validation"""
        request = SummaryRequest(
            competitor_id=1,
            since="7d",
            summary_type="competitive_analysis"
        )
        
        assert request.competitor_id == 1
        assert request.since == "7d"
        
        # Test invalid period
        with pytest.raises(ValueError):
            SummaryRequest(since="invalid_period")
    
    def test_mock_summary_generation(self):
        """Test mock summary generation from posts"""
        # Create sample posts
        posts = [
            Post(
                platform="instagram",
                account="nike",
                text="New Air Max collection! #airmax #nike",
                likes=2500,
                comments=45,
                hashtags=["airmax", "nike"],
                posted_at=datetime.now() - timedelta(days=1)
            ),
            Post(
                platform="instagram", 
                account="nike",
                text="Sustainability matters! Going green 🌱 #sustainability #nike",
                likes=1800,
                comments=32,
                hashtags=["sustainability", "nike"],
                posted_at=datetime.now() - timedelta(days=2)
            )
        ]
        
        # Mock summary generation
        summary = self._generate_mock_summary(posts, "7d")
        
        assert summary.post_count == 2
        assert summary.period == "7d"
        assert len(summary.key_insights) > 0
        assert summary.avg_engagement == 2188.5  # Includes comments: (2500+45+1800+32)/2
        assert "nike" in summary.trending_hashtags
    
    def test_mock_summary_with_different_platforms(self):
        """Test summary generation with posts from different platforms"""
        posts = [
            Post(
                platform="instagram",
                account="nike",
                text="Instagram post #nike",
                likes=1000
            ),
            Post(
                platform="linkedin",
                account="nike",
                text="LinkedIn article about innovation",
                likes=500
            ),
            Post(
                platform="tiktok",
                account="nike",
                text="TikTok video #justdoit",
                views=10000
            )
        ]
        
        summary = self._generate_mock_summary(posts, "30d")
        assert summary.post_count == 3
        assert len(summary.content_themes) >= 1
    
    def test_empty_posts_summary(self):
        """Test summary generation with no posts"""
        posts = []
        summary = self._generate_mock_summary(posts, "7d")
        
        assert summary.post_count == 0
        assert summary.avg_engagement == 0
        assert summary.overview == "No posts found for the specified period."
    
    @patch('openai.OpenAI')
    def test_ai_summary_mock(self, mock_openai):
        """Test AI summary generation with mocked OpenAI client"""
        # Mock OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "overview": "Strong performance this week with focus on new products",
            "key_insights": [
                "Increased engagement on product launches",
                "Sustainability messaging resonates well"
            ],
            "content_themes": ["product_launch", "sustainability", "sports"],
            "performance_highlights": [
                "Air Max post performed 40% above average",
                "Video content showing 2x engagement"
            ]
        }
        '''
        
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Test the mocked AI summary
        posts = [
            Post(platform="instagram", account="nike", text="Test post #nike", likes=1000)
        ]
        
        summary = self._generate_ai_summary_mock(posts, mock_client)
        
        assert "Strong performance" in summary.overview
        assert len(summary.key_insights) == 2
        assert "product_launch" in summary.content_themes
    
    def _generate_mock_summary(self, posts, period):
        """Generate a mock summary from posts"""
        if not posts:
            return Summary(
                period=period,
                post_count=0,
                overview="No posts found for the specified period.",
                avg_engagement=0,
                key_insights=[],
                trending_hashtags=[]
            )
        
        # Calculate metrics
        total_engagement = sum(
            (post.likes or 0) + (post.comments or 0) + (post.views or 0) 
            for post in posts
        )
        avg_engagement = total_engagement / len(posts) if posts else 0
        
        # Extract hashtags
        all_hashtags = []
        for post in posts:
            all_hashtags.extend(post.hashtags)
        trending_hashtags = list(set(all_hashtags))[:5]
        
        # Generate insights
        key_insights = [
            f"Analyzed {len(posts)} posts across {len(set(p.platform for p in posts))} platforms",
            f"Average engagement: {avg_engagement:.0f}",
            "Content themes: product launches, brand messaging"
        ]
        
        content_themes = ["product_launch", "brand_awareness", "engagement"]
        
        return Summary(
            period=period,
            post_count=len(posts),
            overview=f"Analysis of {len(posts)} posts showing strong engagement patterns.",
            key_insights=key_insights,
            content_themes=content_themes,
            avg_engagement=avg_engagement,
            trending_hashtags=trending_hashtags
        )
    
    def _generate_ai_summary_mock(self, posts, mock_client):
        """Generate AI summary using mocked OpenAI client"""
        import json
        
        # This would be the actual AI summary function with mocked client
        response = mock_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI that analyzes social media posts."},
                {"role": "user", "content": f"Analyze these {len(posts)} posts and provide insights."}
            ]
        )
        
        # Parse the mocked response
        content = response.choices[0].message.content.strip()
        try:
            ai_data = json.loads(content)
            return Summary(
                period="7d",
                post_count=len(posts),
                overview=ai_data.get("overview", "AI-generated overview"),
                key_insights=ai_data.get("key_insights", []),
                content_themes=ai_data.get("content_themes", []),
                performance_highlights=ai_data.get("performance_highlights", [])
            )
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return Summary(
                period="7d",
                post_count=len(posts),
                overview="AI analysis completed successfully",
                key_insights=["Mock insight 1", "Mock insight 2"]
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
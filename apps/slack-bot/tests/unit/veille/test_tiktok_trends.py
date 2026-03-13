"""
Tests pour l'analyse des tendances TikTok
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.bot.veille.ultra_veille_engine import SocialMediaScraper


class TestTikTokTrendsAnalysis:
    """Tests pour l'analyse des tendances TikTok"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.scraper = SocialMediaScraper()
        self.sample_videos = [
            {
                'id': 'video1',
                'caption': 'Amazing #nike #sport content! Love this #challenge',
                'likes': '1.2K',
                'comments': '45',
                'sentiment': 'positive'
            },
            {
                'id': 'video2',
                'caption': 'Check out this #nike #dance challenge!',
                'likes': '5.2K',
                'comments': '123',
                'sentiment': 'positive'
            },
            {
                'id': 'video3',
                'caption': 'Product review of #nike shoes',
                'likes': '892',
                'comments': '23',
                'sentiment': 'neutral'
            }
        ]
    
    def test_analyze_tiktok_trends_viral_hashtags(self):
        """Test analyse des hashtags viraux"""
        trends = self.scraper.analyze_tiktok_trends(self.sample_videos)
        
        assert 'viral_hashtags' in trends
        assert len(trends['viral_hashtags']) > 0
        
        # Vérifier que nike apparaît le plus souvent
        nike_count = next((h['count'] for h in trends['viral_hashtags'] if h['hashtag'] == 'nike'), 0)
        assert nike_count >= 2
    
    def test_analyze_tiktok_trends_challenges(self):
        """Test détection des challenges"""
        trends = self.scraper.analyze_tiktok_trends(self.sample_videos)
        
        assert 'challenges' in trends
        assert len(trends['challenges']) > 0
        
        # Vérifier qu'on détecte les challenges
        challenge_types = [c['challenge_type'] for c in trends['challenges']]
        assert 'dance' in challenge_types or 'trend' in challenge_types
    
    def test_analyze_tiktok_trends_viral_score(self):
        """Test calcul du score de viralité"""
        trends = self.scraper.analyze_tiktok_trends(self.sample_videos)
        
        assert 'viral_score' in trends
        assert isinstance(trends['viral_score'], float)
        assert 0.0 <= trends['viral_score'] <= 1.0
    
    def test_analyze_tiktok_trends_engagement_patterns(self):
        """Test patterns d'engagement"""
        trends = self.scraper.analyze_tiktok_trends(self.sample_videos)
        
        assert 'engagement_patterns' in trends
        assert 'positive' in trends['engagement_patterns']
        assert 'negative' in trends['engagement_patterns']
        assert 'neutral' in trends['engagement_patterns']
        
        # Vérifier que les patterns sont des nombres
        for sentiment, engagement in trends['engagement_patterns'].items():
            assert isinstance(engagement, int)
            assert engagement >= 0
    
    def test_analyze_tiktok_trends_content_themes(self):
        """Test thèmes de contenu"""
        trends = self.scraper.analyze_tiktok_trends(self.sample_videos)
        
        assert 'content_themes' in trends
        assert len(trends['content_themes']) > 0
        
        # Vérifier qu'on détecte les thèmes
        themes = [t['theme'] for t in trends['content_themes']]
        assert 'product_showcase' in themes or 'general' in themes
    
    def test_analyze_tiktok_trends_empty_data(self):
        """Test avec données vides"""
        trends = self.scraper.analyze_tiktok_trends([])
        
        assert 'viral_hashtags' in trends
        assert 'challenges' in trends
        assert 'viral_score' in trends
        assert trends['viral_score'] == 0.0
        assert len(trends['viral_hashtags']) == 0
        assert len(trends['challenges']) == 0
    
    def test_analyze_tiktok_trends_large_numbers(self):
        """Test avec de grands nombres (K, M)"""
        videos_with_large_numbers = [
            {
                'id': 'video1',
                'caption': 'Amazing #nike content!',
                'likes': '1.2M',
                'comments': '45K',
                'sentiment': 'positive'
            }
        ]
        
        trends = self.scraper.analyze_tiktok_trends(videos_with_large_numbers)
        
        assert trends['viral_score'] > 0.0
        assert trends['engagement_patterns']['positive'] > 0
    
    def test_analyze_tiktok_trends_mixed_content(self):
        """Test avec contenu mixte"""
        mixed_videos = [
            {
                'id': 'video1',
                'caption': 'Product showcase of #nike shoes',
                'likes': '1K',
                'comments': '50',
                'sentiment': 'positive'
            },
            {
                'id': 'video2',
                'caption': 'How to style #nike sneakers tutorial',
                'likes': '2K',
                'comments': '100',
                'sentiment': 'positive'
            },
            {
                'id': 'video3',
                'caption': 'Review of #nike performance',
                'likes': '500',
                'comments': '25',
                'sentiment': 'neutral'
            }
        ]
        
        trends = self.scraper.analyze_tiktok_trends(mixed_videos)
        
        # Vérifier qu'on détecte différents thèmes
        themes = [t['theme'] for t in trends['content_themes']]
        assert 'product_showcase' in themes
        assert 'tutorial' in themes
        assert 'review' in themes
    
    def test_analyze_tiktok_trends_negative_sentiment(self):
        """Test avec sentiment négatif"""
        negative_videos = [
            {
                'id': 'video1',
                'caption': 'Hate this #nike product, terrible quality',
                'likes': '100',
                'comments': '200',
                'sentiment': 'negative'
            }
        ]
        
        trends = self.scraper.analyze_tiktok_trends(negative_videos)
        
        assert trends['engagement_patterns']['negative'] > 0
        assert trends['engagement_patterns']['positive'] == 0
    
    def test_analyze_tiktok_trends_hashtag_extraction(self):
        """Test extraction des hashtags"""
        videos_with_hashtags = [
            {
                'id': 'video1',
                'caption': 'Check out #nike #sport #fitness #workout',
                'likes': '1K',
                'comments': '50',
                'sentiment': 'positive'
            }
        ]
        
        trends = self.scraper.analyze_tiktok_trends(videos_with_hashtags)
        
        hashtags = [h['hashtag'] for h in trends['viral_hashtags']]
        assert 'nike' in hashtags
        assert 'sport' in hashtags
        assert 'fitness' in hashtags
        assert 'workout' in hashtags


if __name__ == "__main__":
    pytest.main([__file__]) 
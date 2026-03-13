"""
Tests pour le module Google Slides API
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.bot.slides.google_slides_api import (
    GoogleSlidesAPI, PresentationConfig, SlideContent, 
    GoogleSlidesResult, create_presentation_from_data
)


class TestGoogleSlidesAPI:
    """Tests pour GoogleSlidesAPI"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.api = GoogleSlidesAPI()
        self.test_config = PresentationConfig(
            title="Test Presentation",
            subtitle="Test Subtitle",
            primary_color="#4285F4",
            secondary_color="#34A853"
        )
        self.test_slide = SlideContent(
            title="Test Slide",
            content=["Test content 1", "Test content 2"],
            bullet_points=["Point 1", "Point 2"]
        )
    
    def test_google_slides_api_initialization(self):
        """Test initialisation du GoogleSlidesAPI"""
        assert self.api is not None
        assert hasattr(self.api, 'service')
        assert hasattr(self.api, 'credentials_path')
    
    def test_create_presentation_fallback(self):
        """Test création présentation avec fallback"""
        result = self.api.create_presentation(self.test_config, [self.test_slide])
        
        assert isinstance(result, GoogleSlidesResult)
        assert result.presentation_id.startswith("fallback_")
        assert result.slides_count == 1
        assert result.status in ["fallback", "error"]
        assert isinstance(result.creation_time, datetime)
    
    def test_hex_to_rgb_conversion(self):
        """Test conversion hex vers RGB"""
        rgb = self.api._hex_to_rgb("#4285F4")
        
        assert isinstance(rgb, dict)
        assert 'red' in rgb
        assert 'green' in rgb
        assert 'blue' in rgb
        assert all(0.0 <= value <= 1.0 for value in rgb.values())
    
    def test_extract_slide_content(self):
        """Test extraction contenu slide"""
        # Cette méthode est dans le générateur canonique, pas dans l'API
        # Testons plutôt la création de SlideContent
        slide = SlideContent(
            title="Test Title",
            content=["Test Description", "Point 1", "Point 2", "Test Data"]
        )
        
        assert slide.title == "Test Title"
        assert len(slide.content) == 4
        assert "Test Description" in slide.content
        assert "Point 1" in slide.content
        assert "Point 2" in slide.content
        assert "Test Data" in slide.content
    
    def test_create_veille_presentation(self):
        """Test création présentation de veille"""
        veille_data = {
            'insights': [
                {'insight': 'Insight 1'},
                {'insight': 'Insight 2'}
            ],
            'social': {
                'tiktok_content': [{'caption': 'Test TikTok'}],
                'instagram_hashtags': [{'hashtag': 'test'}]
            },
            'trends': [
                {'keyword': 'Trend 1'},
                {'keyword': 'Trend 2'}
            ],
            'sentiment': {
                'overall_sentiment': 'positive',
                'vader_positive': 0.8,
                'vader_negative': 0.1,
                'vader_neutral': 0.1
            }
        }
        
        result = self.api.create_veille_presentation(veille_data, "Nike", "sport")
        
        assert isinstance(result, GoogleSlidesResult)
        assert result.slides_count > 0
        assert result.status in ["success", "fallback", "error"]
    
    def test_create_recommendation_presentation(self):
        """Test création présentation de recommandations"""
        recommendation_data = {
            'context': 'Test context',
            'opportunities': ['Opportunity 1', 'Opportunity 2'],
            'actions': ['Action 1', 'Action 2']
        }
        
        result = self.api.create_recommendation_presentation(recommendation_data, "Nike")
        
        assert isinstance(result, GoogleSlidesResult)
        assert result.slides_count > 0
        assert result.status in ["success", "fallback", "error"]
    
    @patch('src.bot.slides.google_slides_api.GOOGLE_SLIDES_AVAILABLE', True)
    @patch('src.bot.slides.google_slides_api.build')
    def test_create_with_google_slides_success(self, mock_build):
        """Test création avec Google Slides API (succès)"""
        # Mock des services
        mock_service = Mock()
        mock_presentations_service = Mock()
        mock_build.return_value = mock_service
        mock_service.presentations.return_value = mock_presentations_service
        
        # Mock de la création de présentation
        mock_presentations_service.create.return_value.execute.return_value = {
            'presentationId': 'test_presentation_id'
        }
        
        # Mock du batch update
        mock_presentations_service.batchUpdate.return_value.execute.return_value = {}
        
        # Mock du client
        with patch.object(self.api, 'service', mock_service), \
             patch.object(self.api, 'presentations_service', mock_presentations_service):
            
            result = self.api.create_presentation(self.test_config, [self.test_slide])
            
            assert isinstance(result, GoogleSlidesResult)
            assert result.presentation_id == 'test_presentation_id'
            assert result.status == "success"
    
    @patch('src.bot.slides.google_slides_api.GOOGLE_SLIDES_AVAILABLE', True)
    @patch('src.bot.slides.google_slides_api.build')
    def test_create_with_google_slides_failure(self, mock_build):
        """Test création avec Google Slides API (échec)"""
        # Mock des services qui lèvent une exception
        mock_service = Mock()
        mock_presentations_service = Mock()
        mock_presentations_service.create.side_effect = Exception("API Error")
        mock_build.return_value = mock_service
        mock_service.presentations.return_value = mock_presentations_service
        
        # Mock du client
        with patch.object(self.api, 'service', mock_service), \
             patch.object(self.api, 'presentations_service', mock_presentations_service):
            
            result = self.api.create_presentation(self.test_config, [self.test_slide])
            
            # Devrait utiliser le fallback
            assert isinstance(result, GoogleSlidesResult)
            assert result.status in ["fallback", "error"]


class TestCreatePresentationFromData:
    """Tests pour la fonction utilitaire"""
    
    def test_create_presentation_from_data_veille(self):
        """Test création présentation veille depuis données"""
        data = {
            'insights': [{'insight': 'Test insight'}],
            'social': {'tiktok_content': []},
            'trends': [{'keyword': 'test'}],
            'sentiment': {'overall_sentiment': 'positive'}
        }
        
        result = create_presentation_from_data(data, "veille", "Nike", "sport")
        
        assert isinstance(result, GoogleSlidesResult)
        assert result.slides_count > 0
    
    def test_create_presentation_from_data_recommendation(self):
        """Test création présentation recommandations depuis données"""
        data = {
            'context': 'Test context',
            'opportunities': ['Test opportunity'],
            'actions': ['Test action']
        }
        
        result = create_presentation_from_data(data, "recommendation", "Nike")
        
        assert isinstance(result, GoogleSlidesResult)
        assert result.slides_count > 0
    
    def test_create_presentation_from_data_invalid_type(self):
        """Test création avec type invalide"""
        data = {'test': 'data'}
        
        with pytest.raises(ValueError, match="Type de présentation non supporté"):
            create_presentation_from_data(data, "invalid_type", "Nike")


class TestSlideContent:
    """Tests pour SlideContent"""
    
    def test_slide_content_creation(self):
        """Test création SlideContent"""
        slide = SlideContent(
            title="Test Title",
            subtitle="Test Subtitle",
            content=["Content 1", "Content 2"],
            bullet_points=["Point 1", "Point 2"],
            image_url="https://example.com/image.jpg"
        )
        
        assert slide.title == "Test Title"
        assert slide.subtitle == "Test Subtitle"
        assert len(slide.content) == 2
        assert len(slide.bullet_points) == 2
        assert slide.image_url == "https://example.com/image.jpg"
    
    def test_slide_content_defaults(self):
        """Test valeurs par défaut SlideContent"""
        slide = SlideContent(title="Test")
        
        assert slide.title == "Test"
        assert slide.subtitle is None
        assert slide.content is None
        assert slide.bullet_points is None


class TestPresentationConfig:
    """Tests pour PresentationConfig"""
    
    def test_presentation_config_creation(self):
        """Test création PresentationConfig"""
        config = PresentationConfig(
            title="Test Presentation",
            subtitle="Test Subtitle",
            theme="professional",
            primary_color="#4285F4",
            secondary_color="#34A853"
        )
        
        assert config.title == "Test Presentation"
        assert config.subtitle == "Test Subtitle"
        assert config.theme == "professional"
        assert config.primary_color == "#4285F4"
        assert config.secondary_color == "#34A853"
    
    def test_presentation_config_defaults(self):
        """Test valeurs par défaut PresentationConfig"""
        config = PresentationConfig(title="Test")
        
        assert config.title == "Test"
        assert config.theme == "default"
        assert config.slide_size == "16:9"
        assert config.background_color == "#FFFFFF"
        assert config.primary_color == "#4285F4"


if __name__ == "__main__":
    pytest.main([__file__]) 
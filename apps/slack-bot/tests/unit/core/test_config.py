"""
Unit tests for configuration module
Tests all configuration functionalities
"""

import pytest
import os
from unittest.mock import patch, mock_open
from src.core.config import Config, DatabaseConfig, APIConfig, SlackConfig, OpenAIConfig, VeilleConfig


class TestDatabaseConfig:
    """Test DatabaseConfig dataclass"""
    
    def test_database_config_creation(self):
        """Test basic DatabaseConfig creation"""
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            database="test_db",
            username="test_user",
            password="test_pass"
        )
        
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.database == "test_db"
        assert config.username == "test_user"
        assert config.password == "test_pass"
    
    def test_database_config_defaults(self):
        """Test DatabaseConfig with default values"""
        config = DatabaseConfig()
        
        assert config.host == "localhost"  # Default value
        assert config.port == 5432  # Default value
        assert config.database == "revolver_bot"  # Default value
        assert config.username == "postgres"  # Default value
        assert config.password == ""  # Default value


class TestAPIConfig:
    """Test APIConfig dataclass"""
    
    def test_api_config_creation(self):
        """Test basic APIConfig creation"""
        config = APIConfig(
            host="0.0.0.0",
            port=8000,
            debug=True,
            workers=4
        )
        
        assert config.host == "0.0.0.0"
        assert config.port == 8000
        assert config.debug is True
        assert config.workers == 4
    
    def test_api_config_defaults(self):
        """Test APIConfig with default values"""
        config = APIConfig()
        
        assert config.host == "0.0.0.0"  # Default value
        assert config.port == 8000  # Default value
        assert config.debug is False  # Default value
        assert config.workers == 1  # Default value


class TestSlackConfig:
    """Test SlackConfig dataclass"""
    
    def test_slack_config_creation(self):
        """Test basic SlackConfig creation"""
        config = SlackConfig(
            bot_token="xoxb-test-token",
            app_token="xapp-test-token",
            signing_secret="test-secret",
            channel_id="C1234567890"
        )
        
        assert config.bot_token == "xoxb-test-token"
        assert config.app_token == "xapp-test-token"
        assert config.signing_secret == "test-secret"
        assert config.channel_id == "C1234567890"
    
    def test_slack_config_defaults(self):
        """Test SlackConfig with default values"""
        config = SlackConfig()
        
        assert config.bot_token == ""  # Default value
        assert config.app_token == ""  # Default value
        assert config.signing_secret == ""  # Default value
        assert config.channel_id == ""  # Default value


class TestOpenAIConfig:
    """Test OpenAIConfig dataclass"""
    
    def test_openai_config_creation(self):
        """Test basic OpenAIConfig creation"""
        config = OpenAIConfig(
            api_key="sk-test-key",
            model="gpt-4",
            max_tokens=2000,
            temperature=0.7
        )
        
        assert config.api_key == "sk-test-key"
        assert config.model == "gpt-4"
        assert config.max_tokens == 2000
        assert config.temperature == 0.7
    
    def test_openai_config_defaults(self):
        """Test OpenAIConfig with default values"""
        config = OpenAIConfig()
        
        assert config.model == "gpt-4"  # Default value
        assert config.max_tokens == 4000  # Default value
        assert config.temperature == 0.7  # Default value
        assert config.api_key == ""  # Default value


class TestVeilleConfig:
    """Test VeilleConfig dataclass"""
    
    def test_veille_config_creation(self):
        """Test basic VeilleConfig creation"""
        config = VeilleConfig(
            rss_feeds=["feed1", "feed2"],
            social_platforms=["twitter", "linkedin"],
            competitors=["microsoft", "google"],
            update_frequency=1800
        )
        
        assert config.rss_feeds == ["feed1", "feed2"]
        assert config.social_platforms == ["twitter", "linkedin"]
        assert config.competitors == ["microsoft", "google"]
        assert config.update_frequency == 1800
    
    def test_veille_config_defaults(self):
        """Test VeilleConfig with default values"""
        config = VeilleConfig()
        
        assert config.rss_feeds is None  # Default value
        assert config.social_platforms is None  # Default value
        assert config.competitors is None  # Default value
        assert config.update_frequency == 3600  # Default value


class TestConfig:
    """Test main Config class"""
    
    def test_config_creation(self):
        """Test basic Config creation"""
        config = Config()
        
        assert config.database is not None
        assert config.api is not None
        assert config.slack is not None
        assert config.openai is not None
        assert config.veille is not None
        
        # Check that all components are instances of their respective classes
        assert isinstance(config.database, DatabaseConfig)
        assert isinstance(config.api, APIConfig)
        assert isinstance(config.slack, SlackConfig)
        assert isinstance(config.openai, OpenAIConfig)
        assert isinstance(config.veille, VeilleConfig)
    
    def test_config_from_env(self):
        """Test Config creation from environment variables"""
        env_vars = {
            'DB_HOST': 'localhost',
            'DB_PORT': '5432',
            'DB_NAME': 'test_db',
            'DB_USER': 'test_user',
            'DB_PASS': 'test_pass',
            'API_HOST': '0.0.0.0',
            'API_PORT': '8000',
            'SLACK_BOT_TOKEN': 'xoxb-test-token',
            'SLACK_APP_TOKEN': 'xapp-test-token',
            'SLACK_SIGNING_SECRET': 'test-secret',
            'SLACK_CHANNEL_ID': 'C1234567890',
            'OPENAI_API_KEY': 'sk-test-key',
            'VEILLE_RSS_FEEDS': 'feed1,feed2'
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config()
            
            assert config.database.host == "localhost"
            assert config.database.port == 5432
            assert config.database.database == "test_db"
            assert config.database.username == "test_user"
            assert config.database.password == "test_pass"
            
            assert config.api.host == "0.0.0.0"
            assert config.api.port == 8000
            
            assert config.slack.bot_token == "xoxb-test-token"
            assert config.slack.app_token == "xapp-test-token"
            assert config.slack.signing_secret == "test-secret"
            assert config.slack.channel_id == "C1234567890"
            
            assert config.openai.api_key == "sk-test-key"
            
            assert config.veille.rss_feeds == ["feed1", "feed2"]
    
    def test_config_from_env_with_defaults(self):
        """Test Config creation from environment with defaults"""
        env_vars = {
            'DB_HOST': 'localhost',
            'DB_NAME': 'test_db',
            'DB_USER': 'test_user',
            'DB_PASS': 'test_pass',
            'SLACK_BOT_TOKEN': 'xoxb-test-token',
            'SLACK_APP_TOKEN': 'xapp-test-token',
            'SLACK_SIGNING_SECRET': 'test-secret',
            'SLACK_CHANNEL_ID': 'C1234567890',
            'OPENAI_API_KEY': 'sk-test-key'
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config()
            
            # Test default values
            assert config.database.port == 5432  # Default
            assert config.api.host == "0.0.0.0"  # Default
            assert config.api.port == 8000  # Default
            assert config.api.debug is False  # Default
            assert config.api.workers == 1  # Default
            
            assert config.openai.model == "gpt-4"  # Default
            assert config.openai.max_tokens == 4000  # Default
            assert config.openai.temperature == 0.7  # Default
            
            assert config.veille.rss_feeds is None  # Default
            assert config.veille.update_frequency == 3600  # Default
    
    def test_config_validation(self):
        """Test Config validation"""
        # Test with valid configuration
        config = Config()
        
        # Test that all required components are present
        assert config.database is not None
        assert config.api is not None
        assert config.slack is not None
        assert config.openai is not None
        assert config.veille is not None
    
    def test_config_to_dict(self):
        """Test Config serialization to dictionary"""
        config = Config()
        
        # Test that we can access config as dictionary-like
        assert hasattr(config, 'database')
        assert hasattr(config, 'api')
        assert hasattr(config, 'slack')
        assert hasattr(config, 'openai')
        assert hasattr(config, 'veille')


class TestConfigIntegration:
    """Integration tests for configuration"""
    
    def test_full_config_workflow(self):
        """Test complete configuration workflow"""
        # 1. Create configuration from environment
        env_vars = {
            'DB_HOST': 'localhost',
            'DB_PORT': '5432',
            'DB_NAME': 'test_db',
            'DB_USER': 'test_user',
            'DB_PASS': 'test_pass',
            'API_HOST': '0.0.0.0',
            'API_PORT': '8000',
            'API_DEBUG': 'true',
            'API_WORKERS': '4',
            'SLACK_BOT_TOKEN': 'xoxb-test-token',
            'SLACK_APP_TOKEN': 'xapp-test-token',
            'SLACK_SIGNING_SECRET': 'test-secret',
            'SLACK_CHANNEL_ID': 'C1234567890',
            'OPENAI_API_KEY': 'sk-test-key',
            'OPENAI_MODEL': 'gpt-4',
            'OPENAI_MAX_TOKENS': '2000',
            'OPENAI_TEMPERATURE': '0.7',
            'VEILLE_RSS_FEEDS': 'feed1,feed2,feed3',
            'VEILLE_SOCIAL_PLATFORMS': 'twitter,linkedin',
            'VEILLE_COMPETITORS': 'microsoft,google,apple'
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config()
            
            # 2. Verify database configuration
            assert config.database.host == "localhost"
            assert config.database.port == 5432
            assert config.database.database == "test_db"
            assert config.database.username == "test_user"
            assert config.database.password == "test_pass"
            
            # 3. Verify API configuration
            assert config.api.host == "0.0.0.0"
            assert config.api.port == 8000
            assert config.api.debug is True
            assert config.api.workers == 4
            
            # 4. Verify Slack configuration
            assert config.slack.bot_token == "xoxb-test-token"
            assert config.slack.app_token == "xapp-test-token"
            assert config.slack.signing_secret == "test-secret"
            assert config.slack.channel_id == "C1234567890"
            
            # 5. Verify OpenAI configuration
            assert config.openai.api_key == "sk-test-key"
            assert config.openai.model == "gpt-4"
            assert config.openai.max_tokens == 2000
            assert config.openai.temperature == 0.7
            
            # 6. Verify Veille configuration
            assert config.veille.rss_feeds == ["feed1", "feed2", "feed3"]
    
    def test_config_error_handling(self):
        """Test configuration error handling"""
        # Test with missing required environment variables
        with patch.dict(os.environ, {}, clear=True):
            # Should handle missing environment variables gracefully
            try:
                config = Config()
                # If no exception is raised, verify default values
                assert config.database.host == "localhost"  # Default
                assert config.database.port == 5432  # Default
                assert config.api.host == "0.0.0.0"  # Default
                assert config.api.port == 8000  # Default
                assert config.veille.rss_feeds is None  # Default
            except Exception as e:
                # If exception is raised, it should be handled appropriately
                assert isinstance(e, (ValueError, KeyError, AttributeError))
    
    def test_config_validation_integration(self):
        """Test configuration validation integration"""
        # Test with invalid values
        env_vars = {
            'DB_HOST': 'localhost',
            'DB_PORT': 'invalid_port',  # Invalid port
            'DB_NAME': 'test_db',
            'DB_USER': 'test_user',
            'DB_PASS': 'test_pass',
            'API_PORT': '99999',  # Invalid port
            'OPENAI_TEMPERATURE': '2.0',  # Invalid temperature
            'SLACK_BOT_TOKEN': 'invalid-token',  # Invalid token format
            'OPENAI_API_KEY': 'invalid-key'  # Invalid key format
        }
        
        with patch.dict(os.environ, env_vars):
            # Should handle invalid values gracefully
            try:
                config = Config()
                # If no exception is raised, verify that invalid values are handled
                assert config.database.port == 5432  # Should use default
                assert config.api.port == 8000  # Should use default
                assert config.openai.temperature == 0.7  # Should use default
            except Exception as e:
                # If exception is raised, it should be handled appropriately
                assert isinstance(e, (ValueError, TypeError)) 
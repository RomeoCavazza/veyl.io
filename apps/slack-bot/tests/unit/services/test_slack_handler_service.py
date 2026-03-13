"""
Tests unitaires pour le service de gestionnaire Slack unifié
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.slack_handler_service import (
    SlackHandlerService,
    get_slack_handler_service,
    SlackCommandRequest,
    SlackCommandResponse,
    SlackCommand,
    handle_veille_command,
    handle_analyse_command,
    handle_slack_event
)


class TestSlackHandlerService:
    """Tests pour le service de gestionnaire Slack unifié"""

    @pytest.fixture
    def slack_service(self):
        """Fixture pour le service Slack"""
        return get_slack_handler_service()

    @pytest.mark.asyncio
    async def test_handle_veille_command_success(self, slack_service):
        """Test commande veille réussie"""
        request = SlackCommandRequest(
            command=SlackCommand.VEILLE,
            args=['tech', 'ai']
        )

        with patch('src.bot.orchestrator.run_veille') as mock_run_veille:
            mock_run_veille.return_value = {
                'status': 'success',
                'results': [{'articles': [{'title': 'Test'}]}]
            }

            result = await slack_service.handle_command(request)

            assert result.success is True
            assert "terminée" in result.message.lower()
            mock_run_veille.assert_called_once_with(topics=['tech', 'ai'])

    @pytest.mark.asyncio
    async def test_handle_analyse_command_success(self, slack_service):
        """Test commande analyse réussie"""
        request = SlackCommandRequest(
            command=SlackCommand.ANALYSE,
            args=['data.csv']
        )

        with patch('src.bot.orchestrator.run_analyse') as mock_run_analyse:
            mock_run_analyse.return_value = {'status': 'success'}

            result = await slack_service.handle_command(request)

            assert result.success is True
            assert "terminée" in result.message.lower()
            mock_run_analyse.assert_called_once_with('data.csv')

    @pytest.mark.asyncio
    async def test_handle_brief_command_success(self, slack_service):
        """Test commande brief réussie"""
        request = SlackCommandRequest(
            command=SlackCommand.BRIEF,
            args=['brief.pdf']
        )

        with patch('src.bot.orchestrator.process_brief') as mock_process_brief:
            mock_process_brief.return_value = {'success': True}

            result = await slack_service.handle_command(request)

            assert result.success is True
            assert "traité" in result.message.lower()

    @pytest.mark.asyncio
    async def test_handle_status_command(self, slack_service):
        """Test commande status"""
        request = SlackCommandRequest(
            command=SlackCommand.STATUS,
            args=[]
        )

        result = await slack_service.handle_command(request)

        assert result.success is True
        assert "statut" in result.message.lower()
        assert result.data is not None

    @pytest.mark.asyncio
    async def test_handle_help_command(self, slack_service):
        """Test commande help"""
        request = SlackCommandRequest(
            command=SlackCommand.HELP,
            args=[]
        )

        result = await slack_service.handle_command(request)

        assert result.success is True
        assert "🤖" in result.message  # Emoji présent dans le message d'aide

    @pytest.mark.asyncio
    async def test_handle_unknown_command(self, slack_service):
        """Test commande inconnue"""
        request = SlackCommandRequest(
            command="unknown_command",  # Commande invalide
            args=[]
        )

        result = await slack_service.handle_command(request)

        assert result.success is False
        assert "inconnue" in result.message.lower()

    @pytest.mark.asyncio
    async def test_singleton_pattern(self):
        """Test que get_slack_handler_service retourne toujours la même instance"""
        service1 = get_slack_handler_service()
        service2 = get_slack_handler_service()

        assert service1 is service2


class TestSlackCommandRequest:
    """Tests pour SlackCommandRequest"""

    def test_slack_command_request_creation(self):
        """Test création d'SlackCommandRequest"""
        request = SlackCommandRequest(
            command=SlackCommand.VEILLE,
            args=['arg1', 'arg2'],
            user='test_user',
            channel='test_channel'
        )

        assert request.command == SlackCommand.VEILLE
        assert request.args == ['arg1', 'arg2']
        assert request.user == 'test_user'
        assert request.channel == 'test_channel'
        assert request.timestamp is not None


class TestSlackCommandResponse:
    """Tests pour SlackCommandResponse"""

    def test_slack_command_response_creation(self):
        """Test création d'SlackCommandResponse"""
        response = SlackCommandResponse(
            success=True,
            message="Test message",
            data={'test': 'data'},
            processing_time=1.5
        )

        assert response.success is True
        assert response.message == "Test message"
        assert response.data == {'test': 'data'}
        assert response.processing_time == 1.5
        assert response.timestamp is not None


class TestSlackCommand:
    """Tests pour SlackCommand enum"""

    def test_slack_command_values(self):
        """Test valeurs de l'enum SlackCommand"""
        assert SlackCommand.VEILLE.value == "veille"
        assert SlackCommand.ANALYSE.value == "analyse"
        assert SlackCommand.BRIEF.value == "brief"
        assert SlackCommand.STATUS.value == "status"
        assert SlackCommand.HELP.value == "help"


class TestSlackEventProcessing:
    """Tests pour le traitement des événements Slack"""

    @pytest.fixture
    def slack_service(self):
        """Fixture pour le service Slack"""
        return get_slack_handler_service()

    @pytest.mark.asyncio
    async def test_process_slack_event_valid_command(self, slack_service):
        """Test traitement d'événement Slack avec commande valide"""
        event_data = {
            'text': '!veille tech ai',
            'user': 'test_user',
            'channel': 'test_channel'
        }

        with patch.object(slack_service, 'handle_command', new_callable=AsyncMock) as mock_handle:
            mock_handle.return_value = SlackCommandResponse(
                success=True,
                message="Test response"
            )

            result = await slack_service.process_slack_event(event_data)

            assert result['type'] == 'command_response'
            assert result['success'] is True
            assert result['message'] == 'Test response'
            mock_handle.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_slack_event_invalid_command(self, slack_service):
        """Test traitement d'événement Slack avec commande invalide"""
        event_data = {
            'text': 'invalid command',
            'user': 'test_user'
        }

        result = await slack_service.process_slack_event(event_data)

        assert result['type'] == 'error'
        assert 'Commande doit commencer par !' in result['message']

    @pytest.mark.asyncio
    async def test_process_slack_event_unknown_command(self, slack_service):
        """Test traitement d'événement Slack avec commande inconnue"""
        event_data = {
            'text': '!unknown',
            'user': 'test_user'
        }

        result = await slack_service.process_slack_event(event_data)

        assert result['type'] == 'error'
        assert 'Commande inconnue' in result['message']


class TestCompatibilityFunctions:
    """Tests pour les fonctions de compatibilité"""

    @pytest.mark.asyncio
    async def test_handle_veille_command_function(self):
        """Test fonction de compatibilité handle_veille_command"""
        with patch('src.services.slack_handler_service.get_slack_handler_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.handle_command.return_value = SlackCommandResponse(
                success=True,
                message="Veille terminée"
            )
            mock_get_service.return_value = mock_service

            result = await handle_veille_command()

            assert result == "Veille terminée"

    @pytest.mark.asyncio
    async def test_handle_analyse_command_function(self):
        """Test fonction de compatibilité handle_analyse_command"""
        with patch('src.services.slack_handler_service.get_slack_handler_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.handle_command.return_value = SlackCommandResponse(
                success=False,
                message="Erreur analyse"
            )
            mock_get_service.return_value = mock_service

            result = await handle_analyse_command()

            assert result == "Erreur analyse"

    @pytest.mark.asyncio
    async def test_handle_slack_event_function(self):
        """Test fonction de compatibilité handle_slack_event"""
        with patch('src.services.slack_handler_service.get_slack_handler_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.process_slack_event.return_value = {
                'type': 'test_response',
                'success': True
            }
            mock_get_service.return_value = mock_service

            result = await handle_slack_event({'text': '!test'})

            assert result['type'] == 'test_response'
            assert result['success'] is True
"""
Opérations de base Google Slides
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class GoogleSlidesOperations:
    """Opérations de base pour Google Slides"""

    def __init__(self, service_account_file: Optional[str] = None):
        self.service_account_file = service_account_file
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """Initialise le service Google Slides"""
        try:
            if not self.service_account_file:
                self.service_account_file = "service_account.json"

            from googleapiclient.discovery import build
            from google.oauth2 import service_account

            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_file,
                scopes=['https://www.googleapis.com/auth/presentations']
            )

            self.service = build('slides', 'v1', credentials=credentials)
            logger.info("✅ Google Slides service initialized")

        except Exception as e:
            logger.warning(f"❌ Failed to initialize Google Slides service: {e}")
            self.service = None

    def create_presentation(self, title: str) -> Optional[str]:
        """Crée une nouvelle présentation"""
        if not self.service:
            return None

        try:
            presentation = {
                'title': title
            }

            result = self.service.presentations().create(body=presentation).execute()
            presentation_id = result.get('presentationId')

            logger.info(f"✅ Presentation created: {presentation_id}")
            return presentation_id

        except Exception as e:
            logger.error(f"❌ Error creating presentation: {e}")
            return None

    def add_slide(self, presentation_id: str, slide_content: Dict) -> bool:
        """Ajoute une slide à la présentation"""
        if not self.service:
            return False

        try:
            # Créer la requête pour ajouter une slide
            requests = [{
                'createSlide': {
                    'slideLayoutReference': {
                        'predefinedLayout': 'TITLE_AND_BODY'
                    }
                }
            }]

            # Exécuter la requête
            self.service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={'requests': requests}
            ).execute()

            logger.info(f"✅ Slide added to presentation {presentation_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error adding slide: {e}")
            return False

    def update_slide_content(self, presentation_id: str, slide_id: str, content: Dict) -> bool:
        """Met à jour le contenu d'une slide"""
        if not self.service:
            return False

        try:
            requests = []

            # Ajouter le titre
            if 'title' in content:
                requests.append({
                    'insertText': {
                        'objectId': slide_id,
                        'text': content['title']
                    }
                })

            # Ajouter le contenu
            if 'content' in content:
                for item in content['content']:
                    requests.append({
                        'insertText': {
                            'objectId': slide_id,
                            'text': item
                        }
                    })

            if requests:
                self.service.presentations().batchUpdate(
                    presentationId=presentation_id,
                    body={'requests': requests}
                ).execute()

            logger.info(f"✅ Slide content updated: {slide_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error updating slide content: {e}")
            return False

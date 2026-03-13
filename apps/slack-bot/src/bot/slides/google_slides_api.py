class GoogleSlidesAPI:
    """API Google Slides pour génération automatique"""
    
    def __init__(self, credentials_path: Optional[str] = None):
        self.credentials_path = credentials_path or os.getenv('GOOGLE_CREDENTIALS_FILE')

        # Utilisation du module spécialisé pour les opérations
        self.operations = GoogleSlidesOperations(self.credentials_path)

        # Fallback mode si Google Slides n'est pas disponible
        self.fallback_mode = not GOOGLE_SLIDES_AVAILABLE or not self.credentials_path

        if not self.fallback_mode:
            logger.info("✅ Google Slides API initialized")
        else:
            logger.info("⚠️ Google Slides API in fallback mode")
    
    def create_presentation(self, config: PresentationConfig, slides_content: List[SlideContent]) -> GoogleSlidesResult:
        """Crée une présentation complète"""
        try:
            if not self.fallback_mode:
                return self._create_with_google_slides(config, slides_content)
            else:
                return self._create_with_fallback(config, slides_content)
        except Exception as e:
            logger.error(f"Erreur création présentation: {e}")
            return GoogleSlidesResult(
                success=False,
                error_message=str(e)
            )
    
    def _create_with_google_slides(self, config: PresentationConfig, slides_content: List[SlideContent]) -> GoogleSlidesResult:
        """Crée une présentation avec Google Slides API"""
        try:
            # Créer la présentation avec le module operations
            presentation_id = self.operations.create_presentation(config.title)

            if not presentation_id:
                return GoogleSlidesResult(
                    success=False,
                    error_message="Failed to create presentation"
                )
            
            # Ajouter les slides avec le module operations
            for slide_content in slides_content:
                slide_data = {
                    'title': slide_content.title,
                    'content': slide_content.content or []
                }
                self.operations.add_slide(presentation_id, slide_data)

            # Créer l'URL de la présentation
            presentation_url = f"https://docs.google.com/presentation/d/{presentation_id}/edit"

            return GoogleSlidesResult(
                success=True,
                presentation_id=presentation_id,
                presentation_url=presentation_url,
                slide_count=len(slides_content)
            )
            
        except HttpError as error:
            logger.error(f"Erreur Google Slides API: {error}")
            return GoogleSlidesResult(
                presentation_id="error",
                presentation_url="",
                slides_count=0,
                creation_time=datetime.now(),
                status="error",
                error_message=str(error)
            )
    
    def _create_theme_requests(self, config: PresentationConfig) -> List[Dict]:
        """Crée les requêtes pour le thème"""
        requests = []
        
        # Configuration des couleurs
        color_requests = [
            {
                'updatePageProperties': {
                    'objectId': 'presentation',
                    'pageProperties': {
                        'colorScheme': {
                            'colors': [
                                {'opaqueColor': {'rgbColor': self._hex_to_rgb(config.background_color)}},
                                {'opaqueColor': {'rgbColor': self._hex_to_rgb(config.primary_color)}},
                                {'opaqueColor': {'rgbColor': self._hex_to_rgb(config.secondary_color)}}
                            ]

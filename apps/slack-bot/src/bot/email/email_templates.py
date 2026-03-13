"""
Templates Email
Module spécialisé pour la gestion des templates
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import jinja2
import markdown

logger = logging.getLogger(__name__)

class EmailTemplate:
    """Gestionnaire de templates email spécialisé"""

    def __init__(self, template_dir: str = "templates/email"):
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(exist_ok=True)

        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.template_dir)),
            autoescape=True
        )

        # Templates par défaut
        self._create_default_templates()

    def _create_default_templates(self):
        """Crée les templates par défaut si ils n'existent pas"""
        default_templates = {
            'newsletter.html': self._get_newsletter_template(),
            'report.html': self._get_report_template(),
            'alert.html': self._get_alert_template()
        }

        for template_name, content in default_templates.items():
            template_path = self.template_dir / template_name
            if not template_path.exists():
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Created default template: {template_name}")

    def render_newsletter(self, newsletter_data: Dict[str, Any]) -> str:
        """Rend un template de newsletter"""
        try:
            template = self.env.get_template('newsletter.html')
            return template.render(**newsletter_data)
        except jinja2.TemplateNotFound:
            logger.warning("Newsletter template not found, using default")
            return self._render_default_newsletter(newsletter_data)

    def render_report(self, report_data: Dict[str, Any]) -> str:
        """Rend un template de rapport"""
        try:
            template = self.env.get_template('report.html')
            return template.render(**report_data)
        except jinja2.TemplateNotFound:
            logger.warning("Report template not found, using default")
            return self._render_default_report(report_data)

    def render_alert(self, alert_data: Dict[str, Any]) -> str:
        """Rend un template d'alerte"""
        try:
            template = self.env.get_template('alert.html')
            return template.render(**alert_data)
        except jinja2.TemplateNotFound:
            logger.warning("Alert template not found, using default")
            return self._render_default_alert(alert_data)

    def render_custom(self, template_name: str, data: Dict[str, Any]) -> str:
        """Rend un template personnalisé"""
        try:
            template = self.env.get_template(template_name)
            return template.render(**data)
        except jinja2.TemplateNotFound:
            raise ValueError(f"Template {template_name} not found")

    def create_template(self, name: str, content: str):
        """Crée un nouveau template"""
        template_path = self.template_dir / f"{name}.html"
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Created template: {name}")

    def list_templates(self) -> list:
        """Liste tous les templates disponibles"""
        return [f.stem for f in self.template_dir.glob('*.html')]

    def markdown_to_html(self, markdown_content: str) -> str:
        """Convertit du Markdown en HTML"""
        return markdown.markdown(markdown_content)

    def _get_newsletter_template(self) -> str:
        """Template HTML par défaut pour newsletter"""
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        .header { background: #007bff; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
        .content { padding: 20px; line-height: 1.6; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ title }}</h1>
            <p>{{ date }}</p>
        </div>
        <div class="content">
            {{ content|safe }}
        </div>
        <div class="footer">
            <p>Revolver AI Bot - Newsletter</p>
        </div>
    </div>
</body>
</html>"""

    def _get_report_template(self) -> str:
        """Template HTML par défaut pour rapport"""
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        .header { background: #28a745; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 4px; }
        .metric { display: inline-block; margin: 10px; padding: 10px; background: #f8f9fa; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ title }}</h1>
            <p>Généré le {{ date }}</p>
        </div>
        {% for section in sections %}
        <div class="section">
            <h2>{{ section.title }}</h2>
            <div>{{ section.content|safe }}</div>
        </div>
        {% endfor %}
    </div>
</body>
</html>"""

    def _get_alert_template(self) -> str:
        """Template HTML par défaut pour alerte"""
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Alerte: {{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        .alert { background: #dc3545; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
        .content { padding: 20px; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="container">
        <div class="alert">
            <h1>🚨 {{ title }}</h1>
        </div>
        <div class="content">
            <p><strong>Message:</strong> {{ message }}</p>
            <p><strong>Date:</strong> {{ date }}</p>
            {% if details %}
            <p><strong>Détails:</strong> {{ details }}</p>
            {% endif %}
        </div>
    </div>
</body>
</html>"""

    def _render_default_newsletter(self, data: Dict[str, Any]) -> str:
        """Rend une newsletter avec le template par défaut"""
        default_date = datetime.now().strftime('%Y-%m-%d')
        return f"""<!DOCTYPE html>
<html>
<head><title>{data.get('title', 'Newsletter')}</title></head>
<body>
    <h1>{data.get('title', 'Newsletter')}</h1>
    <p>{data.get('date', default_date)}</p>
    <div>{data.get('content', 'Contenu de la newsletter')}</div>
</body>
</html>"""

    def _render_default_report(self, data: Dict[str, Any]) -> str:
        """Rend un rapport avec le template par défaut"""
        default_date = datetime.now().strftime('%Y-%m-%d')
        return f"""<!DOCTYPE html>
<html>
<head><title>{data.get('title', 'Rapport')}</title></head>
<body>
    <h1>{data.get('title', 'Rapport')}</h1>
    <p>Généré le {data.get('date', default_date)}</p>
    <div>{data.get('content', 'Contenu du rapport')}</div>
</body>
</html>"""

    def _render_default_alert(self, data: Dict[str, Any]) -> str:
        """Rend une alerte avec le template par défaut"""
        default_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        default_message = 'Message d\'alerte'
        return f"""<!DOCTYPE html>
<html>
<head><title>Alerte</title></head>
<body>
    <h1>{data.get('title', 'Alerte')}</h1>
    <p>{data.get('message', default_message)}</p>
    <p>Date: {data.get('date', default_date)}</p>
</body>
</html>"""

# Fonction de compatibilité
def get_email_template_manager(template_dir: str = "templates/email") -> EmailTemplate:
    """Retourne un gestionnaire de templates email"""
    return EmailTemplate(template_dir)

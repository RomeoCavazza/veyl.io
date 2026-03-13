import click
from pathlib import Path
from typing import Optional

from src.bot.cli.utils import validate_file_path, ensure_dir
from src.utils.logger_v2 import logger

@click.group()
def cli():
    """CLI pour le bot Revolver AI."""
    pass

@cli.command()
@click.argument('brief_path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Chemin de sortie pour le brief traité')

def report(brief_path: str, output_path: str):
    """Génère un rapport à partir d'un brief."""
    try:
        validate_file_path(brief_path)
        ensure_dir(Path(output_path).parent)
        logger.info(f"Génération du rapport: {brief_path} -> {output_path}")
        # TODO: Implémenter la génération du rapport
        return {"status": "success", "message": "Rapport généré avec succès"}
    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport: {e}")
        raise click.ClickException(str(e))

if __name__ == '__main__':
    cli()

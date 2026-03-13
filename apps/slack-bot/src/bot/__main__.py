#!/usr/bin/env python3
"""
Revolver AI Bot - Point d'entrée principal
"""

import sys
import os
import argparse
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.bot.orchestrator import main as orchestrator_main


def parse_arguments():
    """Parse les arguments de ligne de commande - refactorisé pour réduire la complexité"""
    parser = _create_argument_parser()

    # Configuration des groupes d'arguments
    _add_mode_arguments(parser)
    _add_common_arguments(parser)

    return parser.parse_args()

def _create_argument_parser():
    """Crée le parser d'arguments avec la description"""
    return argparse.ArgumentParser(
        description="Revolver AI Bot - Agent de veille concurrentielle et génération de livrables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python -m src.bot --brief mon_brief.pdf
  python -m src.bot --veille --competitors 15
  python -m src.bot --analyse data/veille/weekly_20250716_212900.json
  python -m src.bot --report --output rapport.pptx
        """
    )

def _add_mode_arguments(parser):
    """Ajoute les arguments de mode d'exécution"""
    mode_group = parser.add_mutually_exclusive_group(required=True)

    mode_group.add_argument(
        '--brief',
        metavar='FILE',
        help='Traiter un brief PDF/JSON'
    )
    mode_group.add_argument(
        '--veille',
        nargs='?',
        const='default',
        metavar='OUTPUT_PATH',
        help='Lancer la veille concurrentielle'
    )
    mode_group.add_argument(
        '--analyse',
        metavar='DATA_FILE',
        help='Analyser des données de veille (CSV/JSON)'
    )
    mode_group.add_argument(
        '--report',
        metavar='BRIEF_FILE',
        help='Générer un rapport complet'
    )

def _add_common_arguments(parser):
    """Ajoute les arguments communs"""
    parser.add_argument(
        '--output',
        metavar='DIR',
        help='Répertoire de sortie'
    )
    parser.add_argument(
        '--config',
        metavar='FILE',
        help='Fichier de configuration'
    )
    parser.add_argument(
        '--competitors',
        type=int,
        default=15,
        help='Nombre de concurrents à analyser (défaut: 15)'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Mode verbeux'
    )


def main():
    """Point d'entrée principal du bot - refactorisé"""
    try:
        # Étape 1: Parser et configurer
        args, mode, brief_path, data_path, output_dir, config = _parse_and_setup()

        # Étape 2: Déterminer le mode et les paramètres
        mode, brief_path, data_path, config = _determine_mode(
            args, mode, brief_path, data_path, config
        )

        # Étape 3: Valider les fichiers
        _validate_files(brief_path, data_path)

        # Étape 4: Exécuter l'opération
        result = _execute_operation(mode, brief_path, data_path, output_dir, config)

        # Étape 5: Afficher le résultat
        _display_result(result, args.verbose)

        return result

    except Exception as e:
        return _handle_error(e)

def _parse_and_setup():
    """Parse les arguments et configure l'environnement"""
    args = parse_arguments()

    if args.verbose:
        print("🔍 Mode verbeux activé")
        print(f"Arguments reçus: {args}")

    return args, None, None, None, args.output, {}

def _determine_mode(args, mode, brief_path, data_path, config):
    """Détermine le mode d'opération et ses paramètres"""
    if args.brief:
        mode = "brief"
        brief_path = args.brief
        print(f"📄 Traitement du brief: {brief_path}")

    elif args.veille:
        mode = "veille"
        if args.veille != 'default':
            data_path = args.veille
        config = {
            'competitors': args.competitors,
            'sources': ['instagram', 'tiktok', 'linkedin', 'rss']
        }
        print(f"📡 Lancement veille concurrentielle ({args.competitors} concurrents)")

    elif args.analyse:
        mode = "analyse"
        data_path = args.analyse
        print(f"📊 Analyse des données: {data_path}")

    elif args.report:
        mode = "report"
        brief_path = args.report
        print(f"📋 Génération rapport: {brief_path}")

    return mode, brief_path, data_path, config

def _validate_files(brief_path, data_path):
    """Valide l'existence des fichiers requis"""
    if brief_path and not os.path.exists(brief_path):
        raise FileNotFoundError(f"Fichier non trouvé: {brief_path}")

    if data_path and not os.path.exists(data_path):
        raise FileNotFoundError(f"Fichier non trouvé: {data_path}")

def _execute_operation(mode, brief_path, data_path, output_dir, config):
    """Exécute l'opération principale via l'orchestrateur"""
    return orchestrator_main(
        mode=mode,
        brief_path=brief_path,
        data_path=data_path,
        output_dir=output_dir,
        config=config
    )

def _display_result(result, verbose):
    """Affiche le résultat de l'opération"""
    if result and result.get('status') == 'success':
        print("✅ Opération terminée avec succès")
        if verbose:
            print(f"Résultat: {result}")
    else:
        print("⚠️ Opération terminée avec des avertissements")
        if verbose:
            print(f"Résultat: {result}")

def _handle_error(error):
    """Gère les erreurs et retourne une réponse d'erreur"""
    if isinstance(error, FileNotFoundError):
        print(f"❌ Erreur fichier: {error}")
    elif isinstance(error, argparse.ArgumentError):
        print(f"❌ Erreur arguments: {error}")
    else:
        print(f"❌ Erreur lors du démarrage du bot: {error}")

    return {"status": "error", "message": str(error)}


if __name__ == "__main__":
    main()

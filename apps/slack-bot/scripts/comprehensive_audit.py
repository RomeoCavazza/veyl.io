#!/usr/bin/env python3
"""
AUDIT COMPREHENSIF DU CODE - Anti-VibeCoding
==========================================

Utilise tous les outils recommandés pour détecter :
- Code mort (vulture)
- Complexité excessive (radon cc)
- Imports inutiles (import checker)
- Duplications (deduplication)
- Patterns spaghetti
- Tests manquants
"""

import os
import re
import ast
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter

class ComprehensiveAuditor:
    """Auditeur complet anti-vibecoding"""

    def __init__(self, src_path: str = "src"):
        self.src_path = Path(src_path)
        self.issues = []
        self.stats = defaultdict(int)

    def run_full_audit(self) -> Dict:
        """Audit complet avec tous les outils"""
        print("🔍 AUDIT COMPREHENSIF ANTI-VIBECODING")
        print("=" * 50)

        results = {
            'dead_code': self.audit_dead_code(),
            'complexity': self.audit_complexity(),
            'imports': self.audit_imports(),
            'duplications': self.audit_duplications(),
            'spaghetti': self.audit_spaghetti(),
            'tests': self.audit_tests_coverage(),
            'hallucinations': self.audit_hallucinations()
        }

        self.print_report(results)
        return results

    def audit_dead_code(self) -> Dict:
        """Audit du code mort avec vulture"""
        print("💀 Audit du code mort (vulture)...")

        try:
            result = subprocess.run(
                ['vulture', 'src/', '--min-confidence', '80'],
                capture_output=True, text=True, timeout=30
            )

            dead_items = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('romeocavazza'):
                    dead_items.append(line.strip())

            return {
                'total_dead_items': len(dead_items),
                'items': dead_items[:20],  # Top 20
                'raw_output': result.stdout
            }
        except Exception as e:
            return {'error': str(e), 'items': []}

    def audit_complexity(self) -> Dict:
        """Audit de complexité avec radon"""
        print("🧠 Audit de complexité (radon)...")

        try:
            result = subprocess.run(
                ['radon', 'cc', 'src/', '--min', 'B'],
                capture_output=True, text=True, timeout=30
            )

            complex_functions = []
            for line in result.stdout.split('\n'):
                if ' - ' in line and any(grade in line for grade in ['B', 'C', 'D', 'E', 'F']):
                    complex_functions.append(line.strip())

            return {
                'complex_functions': complex_functions,
                'total_complex': len(complex_functions)
            }
        except Exception as e:
            return {'error': str(e), 'complex_functions': []}

    def audit_imports(self) -> Dict:
        """Audit des imports"""
        print("📦 Audit des imports...")

        unused_imports = []
        for py_file in self.src_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)

                # Extraire les imports
                imported_names = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imported_names.add(alias.asname or alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        for alias in node.names:
                            imported_names.add(alias.asname or alias.name)

                # Vérifier utilisation
                for name in imported_names:
                    if name not in content and name not in ['os', 'sys', 're']:
                        unused_imports.append({
                            'file': str(py_file),
                            'import': name
                        })

            except Exception as e:
                print(f"❌ Erreur imports {py_file}: {e}")

        return {
            'unused_imports': unused_imports,
            'total_unused': len(unused_imports)
        }

    def audit_duplications(self) -> Dict:
        """Audit des duplications"""
        print("🔄 Audit des duplications...")

        functions = {}
        duplications = []

        for py_file in self.src_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_code = ast.get_source_segment(content, node)
                        if func_code and len(func_code) > 100:  # Fonctions substantielles
                            func_hash = hash(func_code)
                            func_info = {
                                'name': node.name,
                                'file': str(py_file),
                                'code': func_code[:200] + '...' if len(func_code) > 200 else func_code,
                                'hash': func_hash
                            }

                            if func_hash in functions:
                                duplications.append({
                                    'original': functions[func_hash],
                                    'duplicate': func_info
                                })
                            else:
                                functions[func_hash] = func_info

            except Exception as e:
                print(f"❌ Erreur duplications {py_file}: {e}")

        return {
            'total_duplications': len(duplications),
            'duplications': duplications[:10]
        }

    def audit_spaghetti(self) -> Dict:
        """Audit du code spaghetti"""
        print("🍝 Audit du code spaghetti...")

        spaghetti_issues = []

        for py_file in self.src_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                lines = content.split('\n')

                # Détecter fichiers trop longs
                if len(lines) > 1000:
                    spaghetti_issues.append({
                        'file': str(py_file),
                        'issue': f'Fichier trop long ({len(lines)} lignes)',
                        'severity': 'HIGH'
                    })

                # Détecter fonctions trop longues
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_lines = len(ast.get_source_segment(content, node).split('\n'))
                        if func_lines > 50:
                            spaghetti_issues.append({
                                'file': str(py_file),
                                'function': node.name,
                                'issue': f'Fonction trop longue ({func_lines} lignes)',
                                'severity': 'MEDIUM'
                            })

                # Détecter trop de responsabilités dans un fichier
                functions = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
                classes = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])

                if functions > 20 or classes > 10:
                    spaghetti_issues.append({
                        'file': str(py_file),
                        'issue': f'Trop de responsabilités ({functions} fonctions, {classes} classes)',
                        'severity': 'HIGH'
                    })

            except Exception as e:
                print(f"❌ Erreur spaghetti {py_file}: {e}")

        return {
            'spaghetti_issues': spaghetti_issues,
            'total_issues': len(spaghetti_issues)
        }

    def audit_tests_coverage(self) -> Dict:
        """Audit de la couverture de tests"""
        print("🧪 Audit de la couverture de tests...")

        test_files = list(Path('tests').rglob("*.py"))
        src_files = list(self.src_path.rglob("*.py"))

        test_coverage = len(test_files) / len(src_files) if src_files else 0

        missing_tests = []
        for src_file in src_files:
            test_file = Path('tests') / src_file.relative_to(self.src_path)
            if not test_file.exists():
                missing_tests.append(str(src_file))

        return {
            'test_files': len(test_files),
            'src_files': len(src_files),
            'coverage_ratio': test_coverage,
            'missing_tests': missing_tests[:10]  # Top 10
        }

    def audit_hallucinations(self) -> Dict:
        """Audit des hallucinations (imports fantômes, etc.)"""
        print("🦄 Audit des hallucinations...")

        hallucinations = []

        for py_file in self.src_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Détecter imports potentiellement hallucinés
                import_lines = re.findall(r'^(?:import|from) (.+)', content, re.MULTILINE)

                for import_line in import_lines:
                    # Vérifier si c'est un import standard ou installé
                    module = import_line.split()[0].split('.')[0]
                    if module not in ['os', 'sys', 're', 'json', 'datetime', 'typing', 'pathlib', 'functools',
                                    'subprocess', 'tempfile', 'shutil', 'urllib', 'http', 'ssl', 'socket',
                                    'threading', 'multiprocessing', 'concurrent', 'asyncio', 'logging',
                                    'warnings', 'contextlib', 'collections', 'itertools', 'operator',
                                    'functools', 'copy', 'pprint', 'reprlib', 'enum', 'numbers', 'math',
                                    'cmath', 'decimal', 'fractions', 'random', 'statistics', 'datetime',
                                    'calendar', 'time', 'zoneinfo', 'locale', 'gettext', 'argparse',
                                    'optparse', 'getopt', 'readline', 'rlcompleter', 'sqlite3', 'zlib',
                                    'gzip', 'bz2', 'lzma', 'zipfile', 'tarfile', 'csv', 'configparser',
                                    'netrc', 'xdrlib', 'plistlib', 'hashlib', 'hmac', 'secrets', 'ssl',
                                    'socket', 'mmap', 'contextvars', 'concurrent', 'multiprocessing',
                                    'threading', 'asyncio', 'queue', 'sched', '_thread', 'dummy_thread',
                                    'io', 'codecs', 'unicodedata', 'stringprep', 're', 'difflib', 'textwrap',
                                    'string', 'binary', 'struct', 'weakref', 'gc', 'inspect', 'site',
                                    'warnings', 'contextlib', 'abc', 'atexit', 'traceback', 'future',
                                    'keyword', 'ast', 'symtable', 'symbol', 'token', 'tokenize', 'tabnanny',
                                    'pyclbr', 'py_compile', 'compileall', 'dis', 'pickletools', 'platform',
                                    'errno', 'ctypes', 'msvcrt', 'winsound', 'posix', 'pwd', 'spwd', 'grp',
                                    'crypt', 'termios', 'tty', 'pty', 'fcntl', 'pipes', 'resource', 'nis',
                                    'syslog', 'optparse', 'nntplib', 'poplib', 'imaplib', 'smtplib', 'smtpd',
                                    'telnetlib', 'uuid', 'socketserver', 'http', 'ftplib', 'poplib', 'imaplib',
                                    'nntplib', 'smtplib', 'smtpd', 'telnetlib', 'uuid', 'urllib', 'urllib2',
                                    'urlparse', 'cookielib', 'Cookie', 'BaseHTTPServer', 'SimpleHTTPServer',
                                    'CGIHTTPServer', 'wsgiref', 'webbrowser', 'cgi', 'cgitb', 'wsgiref',
                                    'xdrlib', 'plistlib', 'binascii', 'base64', 'binhex', 'uu', 'quopri',
                                    'mailcap', 'mailbox', 'mhlib', 'mimify', 'multifile', 'rfc822', 'formatter']:
                        # Vérifier si le module existe
                        try:
                            __import__(module)
                        except ImportError:
                            hallucinations.append({
                                'file': str(py_file),
                                'import': import_line,
                                'module': module
                            })

            except Exception as e:
                print(f"❌ Erreur hallucinations {py_file}: {e}")

        return {
            'hallucinations': hallucinations,
            'total_hallucinations': len(hallucinations)
        }

    def print_report(self, results: Dict):
        """Afficher le rapport complet"""
        print("\n" + "="*60)
        print("📊 RAPPORT D'AUDIT COMPREHENSIF")
        print("="*60)

        # Code mort
        dead = results['dead_code']
        print(f"\n💀 CODE MORT:")
        print(f"   • Items détectés: {dead.get('total_dead_items', 0)}")
        if dead.get('items'):
            print("   🚨 Exemples:")
            for item in dead['items'][:5]:
                print(f"     • {item}")

        # Complexité
        comp = results['complexity']
        print(f"\n🧠 COMPLEXITÉ:")
        print(f"   • Fonctions complexes: {comp.get('total_complex', 0)}")
        if comp.get('complex_functions'):
            print("   🚨 Fonctions complexes:")
            for func in comp['complex_functions'][:3]:
                print(f"     • {func}")

        # Imports
        imp = results['imports']
        print(f"\n📦 IMPORTS:")
        print(f"   • Imports inutiles: {imp.get('total_unused', 0)}")

        # Duplications
        dup = results['duplications']
        print(f"\n🔄 DUPLICATIONS:")
        print(f"   • Duplications trouvées: {dup.get('total_duplications', 0)}")

        # Spaghetti
        spag = results['spaghetti']
        print(f"\n🍝 CODE SPAGHETTI:")
        print(f"   • Problèmes détectés: {spag.get('total_issues', 0)}")

        # Tests
        tests = results['tests_coverage']
        print(f"\n🧪 TESTS:")
        print(f"   • Ratio couverture: {tests.get('coverage_ratio', 0):.2%}")
        print(f"   • Tests manquants: {len(tests.get('missing_tests', []))}")

        # Hallucinations
        hall = results['hallucinations']
        print(f"\n🦄 HALLUCINATIONS:")
        print(f"   • Imports fantômes: {hall.get('total_hallucinations', 0)}")

        # Recommandations
        print(f"\n🎯 RECOMMANDATIONS PRIORITAIRES:")
        recommendations = self.generate_recommendations(results)
        for i, rec in enumerate(recommendations[:10], 1):
            print(f"   {i}. {rec}")

        print(f"\n✅ Audit terminé - {sum(len(v) if isinstance(v, list) else 0 for v in results.values())} problèmes identifiés")

    def generate_recommendations(self, results: Dict) -> List[str]:
        """Générer des recommandations prioritaires"""
        recommendations = []

        if results['dead_code'].get('total_dead_items', 0) > 0:
            recommendations.append("🧹 Supprimer le code mort détecté par vulture")

        if results['complexity'].get('total_complex', 0) > 0:
            recommendations.append("🔧 Refactoriser les fonctions complexes (grade B+)")

        if results['imports'].get('total_unused', 0) > 0:
            recommendations.append("📦 Nettoyer les imports inutiles")

        if results['duplications'].get('total_duplications', 0) > 0:
            recommendations.append("🔄 Éliminer les duplications de code")

        if results['spaghetti'].get('total_issues', 0) > 0:
            recommendations.append("🍝 Découper les fichiers spaghetti (>1000 lignes)")

        if results['tests_coverage'].get('coverage_ratio', 0) < 0.7:
            recommendations.append("🧪 Augmenter la couverture de tests (>70%)")

        if results['hallucinations'].get('total_hallucinations', 0) > 0:
            recommendations.append("🦄 Corriger les imports hallucinés")

        return recommendations

def main():
    """Fonction principale"""
    auditor = ComprehensiveAuditor()
    results = auditor.run_full_audit()

    # Sauvegarder les résultats
    import json
    with open('comprehensive_audit_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print("\n💾 Résultats sauvegardés dans comprehensive_audit_results.json")

if __name__ == "__main__":
    main()

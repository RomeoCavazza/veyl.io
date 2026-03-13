"""
OSINT sur les réseaux sociaux
"""

import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re

from .osint_models import OSINTResult, OSINTDataType

logger = logging.getLogger(__name__)

class SocialMediaOSINT:
    """OSINT sur les réseaux sociaux"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; OSINT-Bot/1.0)'
        })

    def search_username(self, username: str) -> List[OSINTResult]:
        """Recherche un nom d'utilisateur sur les réseaux sociaux"""
        results = []

        platforms = ['twitter', 'instagram', 'facebook', 'linkedin', 'github']

        for platform in platforms:
            try:
                platform_results = self._search_platform_username(username, platform)
                results.extend(platform_results)
            except Exception as e:
                logger.error(f"Platform search failed for {platform}: {e}")

        return results

    def search_company_social(self, company_name: str) -> List[OSINTResult]:
        """Recherche les présences sociales d'une entreprise"""
        results = []

        try:
            # Recherche sur LinkedIn
            linkedin_results = self._search_linkedin_company(company_name)
            results.extend(linkedin_results)

            # Recherche sur Twitter
            twitter_results = self._search_twitter_company(company_name)
            results.extend(twitter_results)

            # Recherche sur Facebook
            facebook_results = self._search_facebook_company(company_name)
            results.extend(facebook_results)

        except Exception as e:
            logger.error(f"Company social search failed: {e}")

        return results

    def analyze_social_presence(self, target: str, target_type: str = 'company') -> Dict[str, Any]:
        """Analyse complète de la présence sociale"""
        analysis = {
            'target': target,
            'target_type': target_type,
            'platforms_found': [],
            'total_followers': 0,
            'engagement_score': 0.0,
            'last_activity': None,
            'recommendations': []
        }

        if target_type == 'company':
            results = self.search_company_social(target)
        else:
            results = self.search_username(target)

        # Analyse des résultats
        platform_stats = {}
        for result in results:
            platform = result.source
            if platform not in platform_stats:
                platform_stats[platform] = {
                    'count': 0,
                    'followers': 0,
                    'engagement': 0.0
                }

            platform_stats[platform]['count'] += 1
            platform_stats[platform]['followers'] += result.metadata.get('followers', 0)
            platform_stats[platform]['engagement'] = max(
                platform_stats[platform]['engagement'],
                result.metadata.get('engagement_rate', 0.0)
            )

        analysis['platforms_found'] = list(platform_stats.keys())
        analysis['total_followers'] = sum(stats['followers'] for stats in platform_stats.values())
        analysis['engagement_score'] = sum(stats['engagement'] for stats in platform_stats.values()) / max(len(platform_stats), 1)

        # Recommandations
        if len(platform_stats) < 3:
            analysis['recommendations'].append("Consider expanding social media presence")
        if analysis['engagement_score'] < 0.02:
            analysis['recommendations'].append("Improve social media engagement")

        return analysis

    # Méthodes privées pour les recherches par plateforme
    def _search_platform_username(self, username: str, platform: str) -> List[OSINTResult]:
        """Recherche un username sur une plateforme spécifique"""
        results = []

        # Simulation - en pratique utiliserait les APIs officielles
        result = OSINTResult(
            source=platform,
            data_type=OSINTDataType.SOCIAL_MEDIA.value,
            content=f"Profile found for @{username} on {platform}",
            url=f"https://{platform}.com/{username}",
            timestamp=datetime.now(),
            confidence=0.7,
            metadata={
                'username': username,
                'platform': platform,
                'profile_type': 'personal',
                'followers': 150,
                'following': 200,
                'posts_count': 45
            }
        )
        results.append(result)

        return results

    def _search_linkedin_company(self, company_name: str) -> List[OSINTResult]:
        """Recherche d'entreprise sur LinkedIn"""
        results = []

        # Simulation
        result = OSINTResult(
            source="linkedin",
            data_type=OSINTDataType.SOCIAL_MEDIA.value,
            content=f"Company page found for {company_name}",
            url=f"https://linkedin.com/company/{company_name.lower().replace(' ', '-')}",
            timestamp=datetime.now(),
            confidence=0.8,
            metadata={
                'company_name': company_name,
                'platform': 'linkedin',
                'followers': 5000,
                'employees': 150,
                'industry': 'Technology'
            }
        )
        results.append(result)

        return results

    def _search_twitter_company(self, company_name: str) -> List[OSINTResult]:
        """Recherche d'entreprise sur Twitter"""
        results = []

        # Simulation
        result = OSINTResult(
            source="twitter",
            data_type=OSINTDataType.SOCIAL_MEDIA.value,
            content=f"Twitter account found for {company_name}",
            url=f"https://twitter.com/{company_name.lower().replace(' ', '')}",
            timestamp=datetime.now(),
            confidence=0.6,
            metadata={
                'company_name': company_name,
                'platform': 'twitter',
                'followers': 2500,
                'tweets_count': 1200,
                'join_date': '2020-01-01'
            }
        )
        results.append(result)

        return results

    def _search_facebook_company(self, company_name: str) -> List[OSINTResult]:
        """Recherche d'entreprise sur Facebook"""
        results = []

        # Simulation
        result = OSINTResult(
            source="facebook",
            data_type=OSINTDataType.SOCIAL_MEDIA.value,
            content=f"Facebook page found for {company_name}",
            url=f"https://facebook.com/{company_name.lower().replace(' ', '')}",
            timestamp=datetime.now(),
            confidence=0.7,
            metadata={
                'company_name': company_name,
                'platform': 'facebook',
                'likes': 8000,
                'checkins': 450,
                'rating': 4.2
            }
        )
        results.append(result)

        return results

    def get_social_metrics(self, platform: str, username: str) -> Dict[str, Any]:
        """Récupère les métriques sociales d'un profil"""
        # Simulation de métriques
        base_metrics = {
            'followers': 1000,
            'following': 500,
            'posts_count': 200,
            'engagement_rate': 0.03,
            'last_post_date': (datetime.now() - timedelta(days=2)).isoformat()
        }

        # Ajustements par plateforme
        if platform == 'instagram':
            base_metrics.update({
                'followers': base_metrics['followers'] * 2,
                'engagement_rate': 0.05
            })
        elif platform == 'twitter':
            base_metrics.update({
                'followers': base_metrics['followers'] * 1.5,
                'engagement_rate': 0.02
            })

        return base_metrics

    def detect_fake_profiles(self, username: str, platform: str) -> Dict[str, Any]:
        """Détecte les profils suspects/fake"""
        analysis = {
            'username': username,
            'platform': platform,
            'risk_score': 0.0,
            'flags': [],
            'recommendations': []
        }

        # Critères de détection simples
        if len(username) < 4:
            analysis['flags'].append('username_too_short')
            analysis['risk_score'] += 0.3

        if re.search(r'\d{4,}', username):
            analysis['flags'].append('suspicious_numbers')
            analysis['risk_score'] += 0.2

        if analysis['risk_score'] > 0.5:
            analysis['recommendations'].append('High risk of fake profile')
        elif analysis['risk_score'] > 0.2:
            analysis['recommendations'].append('Moderate risk - verify manually')

        return analysis

    def extract_social_insights(self, results: List[OSINTResult]) -> Dict[str, Any]:
        """Extrait des insights des résultats sociaux"""
        insights = {
            'total_platforms': len(set(r.source for r in results)),
            'primary_platform': None,
            'engagement_trends': [],
            'content_themes': [],
            'posting_frequency': 'unknown'
        }

        if results:
            # Plateforme principale
            platform_counts = {}
            for result in results:
                platform_counts[result.source] = platform_counts.get(result.source, 0) + 1

            insights['primary_platform'] = max(platform_counts, key=platform_counts.get)

            # Analyse d'engagement
            total_engagement = sum(r.metadata.get('engagement_rate', 0) for r in results)
            insights['avg_engagement'] = total_engagement / len(results)

        return insights

#!/usr/bin/env python3
"""
Vérifie si les posts sont bien liés au hashtag #fashion dans post_hashtags.
"""
import requests

API_BASE = "https://api.veyl.io"

TOKEN = input("Entre ton token JWT: ").strip()
headers = {"Authorization": f"Bearer {TOKEN}"}

# 1. Trouver le projet "fashion"
print("\n🔍 Recherche du projet 'fashion'...")
response = requests.get(f"{API_BASE}/api/v1/projects", headers=headers)
if response.status_code != 200:
    print(f"❌ Erreur: {response.status_code}")
    exit(1)

projects = response.json()
fashion_project = next((p for p in projects if 'fashion' in p['name'].lower()), None)

if not fashion_project:
    print("❌ Projet 'fashion' introuvable")
    exit(1)

project_id = fashion_project['id']
print(f"✅ Projet trouvé: {fashion_project['name']} (ID: {project_id})")
print(f"   Hashtags: {fashion_project.get('hashtags', [])}")
print(f"   Creators: {fashion_project.get('creators_count', 0)}")
print(f"   Posts count: {fashion_project.get('posts_count', 0)}")

# 2. Récupérer les posts du projet
print("\n📊 Récupération des posts...")
response = requests.get(f"{API_BASE}/api/v1/projects/{project_id}/posts", headers=headers)
if response.status_code != 200:
    print(f"❌ Erreur: {response.status_code}")
    print(response.text)
    exit(1)

posts = response.json()
print(f"✅ {len(posts)} posts trouvés")

if len(posts) == 0:
    print("\n⚠️  AUCUN POST TROUVÉ !")
    print("\n🔍 Diagnostics possibles:")
    print("  1. Le hashtag #fashion n'est pas lié au projet dans project_hashtags")
    print("  2. Les posts ne sont pas liés au hashtag dans post_hashtags")
    print("  3. Les posts n'ont pas de creator lié au projet")
    print("\n💡 Solution: Utilise l'endpoint /api/v1/meta/link-posts-to-hashtag")
    print("   POST /api/v1/meta/link-posts-to-hashtag?hashtag_name=fashion&limit=10")
else:
    print("\n✅ Posts trouvés:")
    for i, post in enumerate(posts[:5], 1):
        print(f"  {i}. @{post.get('author', 'N/A')}: {post.get('caption', 'N/A')[:50]}...")


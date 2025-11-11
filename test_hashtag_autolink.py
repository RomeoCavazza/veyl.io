#!/usr/bin/env python3
"""
Test l'auto-link des posts quand on ajoute un hashtag à un projet.
"""
import requests
import os

API_BASE = "https://api.veyl.io"

# Tu dois avoir un token valide
TOKEN = input("Entre ton token JWT (depuis localStorage): ").strip()

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 1. Créer un projet de test
print("\n📦 Création d'un projet de test...")
response = requests.post(
    f"{API_BASE}/api/v1/projects",
    json={"name": "Test Auto-Link Hashtag", "description": "Test"},
    headers=headers
)

if response.status_code != 201:
    print(f"❌ Erreur création projet: {response.status_code}")
    print(response.text)
    exit(1)

project = response.json()
project_id = project["id"]
print(f"✅ Projet créé: {project_id}")

# 2. Ajouter le hashtag #fashion
print("\n🏷️  Ajout du hashtag #fashion...")
response = requests.post(
    f"{API_BASE}/api/v1/projects/{project_id}/hashtags",
    json={"hashtag": "fashion", "platform": "instagram"},
    headers=headers
)

if response.status_code not in [200, 201]:
    print(f"❌ Erreur ajout hashtag: {response.status_code}")
    print(response.text)
    exit(1)

print("✅ Hashtag ajouté")

# 3. Récupérer les posts du projet
print("\n📊 Récupération des posts du projet...")
response = requests.get(
    f"{API_BASE}/api/v1/projects/{project_id}/posts",
    headers=headers
)

if response.status_code != 200:
    print(f"❌ Erreur récupération posts: {response.status_code}")
    print(response.text)
    exit(1)

posts = response.json()
print(f"✅ {len(posts)} posts trouvés")

if len(posts) > 0:
    print("\n📝 Aperçu des posts:")
    for i, post in enumerate(posts[:5], 1):
        author = post.get('author', 'N/A')
        caption = post.get('caption', 'N/A')[:50]
        print(f"  {i}. @{author}: {caption}...")
else:
    print("⚠️  Aucun post trouvé ! L'auto-link n'a pas fonctionné.")
    print("\n🔍 Vérifications à faire:")
    print("  1. Les posts ont-ils '#fashion' dans leur caption ?")
    print("  2. Le backend a-t-il bien commit les PostHashtag ?")
    print("  3. Regarder les logs Railway pour voir le message '✅ Auto-linked X posts'")

# 4. Nettoyer (optionnel)
cleanup = input("\n🗑️  Supprimer le projet de test ? (y/n): ").strip().lower()
if cleanup == 'y':
    response = requests.delete(
        f"{API_BASE}/api/v1/projects/{project_id}",
        headers=headers
    )
    if response.status_code == 204:
        print("✅ Projet supprimé")
    else:
        print(f"⚠️  Erreur suppression: {response.status_code}")


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Appelle l'endpoint /api/v1/meta/link-posts-to-hashtag
"""
import sys
import requests

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

API_BASE = "https://api.veyl.io/api/v1"

# 1. Login
print("[LOGIN] Connexion...")
login_response = requests.post(
    f"{API_BASE}/auth/login",
    json={
        "email": "romeo.cavazza@gmail.com",
        "password": input("Password: ")  # Demander le mot de passe
    }
)

if login_response.status_code != 200:
    print(f"[ERROR] Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("[OK] Login reussi\n")

# 2. Appeler l'endpoint de liaison
print("[LINK] Liaison des posts au hashtag fashion...")
link_response = requests.post(
    f"{API_BASE}/meta/link-posts-to-hashtag?hashtag_name=fashion&limit=9",
    headers=headers
)

if link_response.status_code != 200:
    print(f"[ERROR] Link failed: {link_response.status_code}")
    print(link_response.text)
    exit(1)

result = link_response.json()
print(f"\n[SUCCESS] {result['message']}")
print(f"  - Hashtag ID: {result['hashtag_id']}")
print(f"  - Total posts: {result['total_posts']}")
print(f"  - Linked: {result['linked_count']}")
print(f"  - Already linked: {result['already_linked']}")

print("\n[DONE] Script completed!")


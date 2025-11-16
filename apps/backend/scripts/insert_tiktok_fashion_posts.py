#!/usr/bin/env python3
"""
Script pour insérer des posts TikTok de démo et les lier au hashtag "fashion"
"""
import os
import sys
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import re

# Ajouter le chemin du backend au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from db.base import get_db
from db.models import Platform, Hashtag, Post, PostHashtag
from core.config import settings

# Données des posts TikTok
TIKTOK_POSTS = [
    {
        "creator": "styledbysash9",
        "url": "https://www.tiktok.com/@styledbysash9/video/7499036976218230038?q=fashion&t=1763320557566"
    },
    {
        "creator": "wisdm8",
        "url": "https://www.tiktok.com/@wisdm8/video/7404270216542244126?q=fashion&t=1763320699290"
    },
    {
        "creator": "yungalyy",
        "url": "https://www.tiktok.com/@yungalyy/video/7509573574215208214?q=fashion&t=1763320699290"
    },
    {
        "creator": "taymosesofficial",
        "url": "https://www.tiktok.com/@taymosesofficial/video/7552842920798276886?q=fashion&t=1763320699290"
    },
    {
        "creator": "reubsfits",
        "url": "https://www.tiktok.com/@reubsfits/video/7522860474103385366?q=fashion&t=1763320699290"
    },
    {
        "creator": "jameswuantin",
        "url": "https://www.tiktok.com/@jameswuantin/video/7568916711970180366?q=fashion&t=1763320870708"
    },
    {
        "creator": "prince_merlin9",
        "url": "https://www.tiktok.com/@prince_merlin9/video/7476098222260276498?q=fashion&t=1763320870708"
    },
    {
        "creator": "vinicci_",
        "url": "https://www.tiktok.com/@vinicci_/video/7525932445175155982?q=fashion&t=1763320870708"
    },
]


def extract_video_id_from_url(url: str) -> str:
    """Extrait le video_id d'une URL TikTok"""
    # Format: https://www.tiktok.com/@username/video/VIDEO_ID?...
    match = re.search(r'/video/(\d+)', url)
    if match:
        return match.group(1)
    raise ValueError(f"Impossible d'extraire le video_id de l'URL: {url}")


def ensure_platform(db: Session, name: str) -> Platform:
    """Assure que la plateforme existe"""
    platform = db.query(Platform).filter(Platform.name == name).first()
    if not platform:
        platform = Platform(name=name)
        db.add(platform)
        db.flush()
        print(f"✅ Créé plateforme: {name}")
    return platform


def ensure_hashtag(db: Session, name: str, platform: Platform) -> Hashtag:
    """Assure que le hashtag existe"""
    hashtag = (
        db.query(Hashtag)
        .filter(Hashtag.name == name, Hashtag.platform_id == platform.id)
        .first()
    )
    if not hashtag:
        hashtag = Hashtag(name=name, platform_id=platform.id, last_scraped=datetime.utcnow())
        db.add(hashtag)
        db.flush()
        print(f"✅ Créé hashtag: #{name} (platform: {platform.name})")
    return hashtag


def upsert_post(
    db: Session,
    platform: Platform,
    video_id: str,
    creator_username: str,
    permalink: str,
) -> Post:
    """Crée ou met à jour un post TikTok"""
    # Utiliser video_id comme id et external_id
    post = db.query(Post).filter(Post.id == video_id).first()
    
    if not post:
        post = Post(
            id=video_id,
            external_id=video_id,
            platform_id=platform.id,
            author=creator_username,
            caption=f"TikTok video by @{creator_username} #fashion",
            permalink=permalink,
            media_url=f"https://p16-sign-va.tiktokcdn.com/obj/tos-maliva-p-0068/placeholder.jpg",  # Placeholder
            posted_at=datetime.utcnow(),
            fetched_at=datetime.utcnow(),
            last_fetch_at=datetime.utcnow(),
            source="tiktok_demo_seed",
            metrics='{"like_count": 0, "comment_count": 0, "view_count": 0}',
            api_payload=f'{{"id": "{video_id}", "creator": "{creator_username}", "url": "{permalink}"}}',
        )
        db.add(post)
        db.flush()
        print(f"✅ Créé post: {video_id} (@{creator_username})")
    else:
        # Mettre à jour si nécessaire
        if not post.permalink:
            post.permalink = permalink
        if not post.author:
            post.author = creator_username
        print(f"ℹ️  Post existant: {video_id} (@{creator_username})")
    
    return post


def link_post_to_hashtag(db: Session, post: Post, hashtag: Hashtag) -> bool:
    """Lie un post à un hashtag (retourne True si créé, False si existait déjà)"""
    existing = (
        db.query(PostHashtag)
        .filter(
            PostHashtag.post_id == post.id,
            PostHashtag.hashtag_id == hashtag.id
        )
        .first()
    )
    
    if existing:
        return False
    
    post_hashtag = PostHashtag(
        post_id=post.id,
        hashtag_id=hashtag.id
    )
    db.add(post_hashtag)
    return True


def main():
    """Fonction principale"""
    print("🚀 Insertion des posts TikTok pour le hashtag #fashion...\n")
    
    # Obtenir une session DB
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        # 1. Assurer que la plateforme TikTok existe
        tiktok_platform = ensure_platform(db, "tiktok")
        db.flush()
        
        # 2. Assurer que le hashtag "fashion" existe pour TikTok
        fashion_hashtag = ensure_hashtag(db, "fashion", tiktok_platform)
        db.flush()
        
        # 3. Traiter chaque post
        created_posts = 0
        linked_posts = 0
        already_linked = 0
        
        for post_data in TIKTOK_POSTS:
            creator = post_data["creator"]
            url = post_data["url"]
            
            try:
                # Extraire le video_id
                video_id = extract_video_id_from_url(url)
                
                # Créer ou mettre à jour le post
                post = upsert_post(
                    db=db,
                    platform=tiktok_platform,
                    video_id=video_id,
                    creator_username=creator,
                    permalink=url.split('?')[0],  # URL sans query params
                )
                db.flush()
                
                # Lier le post au hashtag
                was_created = link_post_to_hashtag(db, post, fashion_hashtag)
                if was_created:
                    linked_posts += 1
                    print(f"  🔗 Lié post {video_id} à #fashion")
                else:
                    already_linked += 1
                    print(f"  ℹ️  Post {video_id} déjà lié à #fashion")
                
                created_posts += 1
                
            except Exception as e:
                print(f"❌ Erreur pour @{creator}: {e}")
                continue
        
        # Commit final
        db.commit()
        
        print(f"\n✅ Terminé!")
        print(f"  - Posts traités: {created_posts}")
        print(f"  - Liens créés: {linked_posts}")
        print(f"  - Déjà liés: {already_linked}")
        print(f"  - Hashtag: #fashion (ID: {fashion_hashtag.id})")
        print(f"  - Plateforme: TikTok (ID: {tiktok_platform.id})")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()


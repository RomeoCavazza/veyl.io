# db/models.py
# Modèles SQLAlchemy pour Insider Trends MVP - VERSION SIMPLIFIÉE PROD
# Architecture minimale et fonctionnelle

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, UniqueConstraint, Float
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship
from db.base import Base
import datetime as dt

# Utiliser Text pour SQLite (compatible avec PostgreSQL aussi)
JSONType = Text
ArrayType = Text

# =====================================================
# 1. UTILISATEURS & AUTHENTIFICATION
# =====================================================

class User(Base):
    """Utilisateur principal du système Insider Trends"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(Text)  # bcrypt hash + salt
    name = Column(String(255))
    picture_url = Column(Text)
    role = Column(String(50), default='user')  # 'admin' / 'analyst' / 'user'
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    last_login_at = Column(DateTime)
    is_active = Column(Boolean, default=True)  # Pour désactiver sans supprimer
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)
    
    # Relations
    oauth_accounts = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")

class OAuthAccount(Base):
    """Comptes OAuth liés aux utilisateurs"""
    __tablename__ = "oauth_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), nullable=False)  # 'google', 'instagram', 'tiktok', 'x'
    provider_user_id = Column(Text, nullable=False)
    access_token = Column(Text)
    refresh_token = Column(Text)
    expires_at = Column(DateTime)
    scopes = Column(ArrayType)  # array des scopes accordés
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="oauth_accounts")
    
    # Contraintes
    __table_args__ = (
        UniqueConstraint('provider', 'provider_user_id', name='uq_oauth_provider_user'),
    )

# =====================================================
# 2. CONTENU SOCIAL - VERSION SIMPLIFIÉE
# =====================================================

class Platform(Base):
    """Plateformes sociales supportées"""
    __tablename__ = "platforms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    api_key = Column(Text)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

class Hashtag(Base):
    """Hashtags surveillés (simplifié - SANS REDONDANCE)"""
    __tablename__ = "hashtags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    last_scraped = Column(DateTime)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)
    
    # Relations
    platform = relationship("Platform")

class PostHashtag(Base):
    """Table de liaison posts-hashtags"""
    __tablename__ = "post_hashtags"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Text, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    hashtag_id = Column(Integer, ForeignKey("hashtags.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    
    # Relations
    post = relationship("Post")
    hashtag = relationship("Hashtag")
    
    # Contraintes
    __table_args__ = (
        UniqueConstraint('post_id', 'hashtag_id', name='uq_post_hashtags'),
    )

class Post(Base):
    """Posts des réseaux sociaux - TOUTE LA LOGIQUE ICI"""
    __tablename__ = "posts"
    
    id = Column(Text, primary_key=True)
    external_id = Column(Text, unique=True, index=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    author = Column(String(255))
    caption = Column(Text)
    hashtags = Column(ArrayType)
    metrics = Column(JSONType)  # likes, comments, shares, views
    posted_at = Column(DateTime)
    fetched_at = Column(DateTime, default=dt.datetime.utcnow)
    language = Column(String(10))
    media_url = Column(Text)
    sentiment = Column(Float)
    score = Column(Float, default=0)
    score_trend = Column(Float, default=0)  # Score de tendance calculé
    api_payload = Column(JSONType)
    last_fetch_at = Column(DateTime)
    source = Column(String(50), default='seed_demo')
    
    # Relations
    platform = relationship("Platform")
    
    # Contraintes
    __table_args__ = (
        UniqueConstraint('platform_id', 'id', name='posts_platform_id_unique'),
        UniqueConstraint('external_id', name='uq_posts_external_id'),
    )

class Subscription(Base):
    """Abonnements et quotas utilisateur"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan = Column(String(50), default='free')
    quota = Column(JSONType)
    renewed_at = Column(DateTime)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    
    # Relations
    user = relationship("User")

# =====================================================
# 3. PROJETS - MONITORING DES TRENDS
# =====================================================

class Project(Base):
    """Projets de monitoring de tendances"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)  # Description du projet (remplace 'goal')
    status = Column(String(50), default='draft')  # 'draft', 'active', 'archived', 'paused'
    
    # Configuration
    platforms = Column(ArrayType)  # JSON: ['instagram', 'tiktok']
    scope_type = Column(String(50))  # 'hashtags', 'creators', 'both'
    scope_query = Column(Text)  # Query originale pour référence
    
    # Métriques cachées (pour performance)
    creators_count = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    signals_count = Column(Integer, default=0)
    
    # Exécution
    last_run_at = Column(DateTime)  # Dernière ingestion
    last_signal_at = Column(DateTime)  # Dernier signal détecté
    
    # Timestamps
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)
    
    # Relations
    user = relationship("User")
    hashtags = relationship("Hashtag", secondary="project_hashtags", backref="projects", overlaps="project,hashtag")
    creators = relationship("ProjectCreator", back_populates="project", cascade="all, delete-orphan")

class ProjectHashtag(Base):
    """Table de liaison projets ↔ hashtags (réutilise table hashtags existante)"""
    __tablename__ = "project_hashtags"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    hashtag_id = Column(Integer, ForeignKey("hashtags.id", ondelete="CASCADE"), nullable=False)
    added_at = Column(DateTime, default=dt.datetime.utcnow)
    
    # Relations avec overlaps pour éviter les warnings SQLAlchemy
    project = relationship("Project", overlaps="hashtags,projects")
    hashtag = relationship("Hashtag", overlaps="projects,hashtags")
    
    # Contraintes
    __table_args__ = (
        UniqueConstraint('project_id', 'hashtag_id', name='uq_project_hashtag'),
    )

class ProjectCreator(Base):
    """Créateurs suivis par projet"""
    __tablename__ = "project_creators"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    creator_username = Column(String(255), nullable=False)  # "@username" ou "username"
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    added_at = Column(DateTime, default=dt.datetime.utcnow)
    
    # Relations
    project = relationship("Project", back_populates="creators")
    platform = relationship("Platform")
    
    # Contraintes
    __table_args__ = (
        UniqueConstraint('project_id', 'platform_id', 'creator_username', name='uq_project_creator'),
    )
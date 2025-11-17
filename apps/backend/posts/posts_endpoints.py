# posts/posts_endpoints.py
from fastapi import APIRouter, Depends, HTTPException, Query  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from typing import List, Optional
from db.base import get_db
from db.models import Post, Platform, User
from auth_unified.auth_endpoints import get_current_user
from .schemas import PostCreate, PostResponse, PostUpdate

posts_router = APIRouter(prefix="/api/v1/posts", tags=["posts"])

@posts_router.get("/", response_model=List[PostResponse])
def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    platform: Optional[str] = Query(None),
    trending: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer les posts avec filtres"""
    query = db.query(Post)
    
    if platform:
        query = query.join(Platform).filter(Platform.name == platform)
    
    if trending:
        query = query.filter(Post.score_trend > 0).order_by(Post.score_trend.desc())
    else:
        query = query.order_by(Post.posted_at.desc())
    
    posts = query.offset(skip).limit(limit).all()
    return posts

@posts_router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer un post par ID"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post non trouvé")
    return post

@posts_router.post("/", response_model=PostResponse)
def create_post(
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un nouveau post"""
    # Vérifier que la plateforme existe
    platform = db.query(Platform).filter(Platform.id == post_in.platform_id).first()
    if not platform:
        raise HTTPException(status_code=400, detail="Plateforme non trouvée")
    
    post = Post(**post_in.dict())
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

@posts_router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: str,
    post_in: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour un post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post non trouvé")
    
    update_data = post_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)
    
    db.commit()
    db.refresh(post)
    return post

@posts_router.delete("/{post_id}")
def delete_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer un post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post non trouvé")
    
    db.delete(post)
    db.commit()
    return {"message": "Post supprimé"}

@posts_router.get("/trending/global", response_model=List[PostResponse])
def get_trending_posts_global(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer les posts les plus tendance globalement"""
    posts = db.query(Post).filter(Post.score_trend > 0).order_by(Post.score_trend.desc()).limit(limit).all()
    return posts

@posts_router.get("/trending/{platform_name}", response_model=List[PostResponse])
def get_trending_posts_platform(
    platform_name: str,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer les posts les plus tendance pour une plateforme"""
    posts = db.query(Post).join(Platform).filter(
        Platform.name == platform_name,
        Post.score_trend > 0
    ).order_by(Post.score_trend.desc()).limit(limit).all()
    return posts

@posts_router.get("/search", response_model=List[PostResponse])
def search_posts(
    q: str = Query(..., min_length=1, description="Terme de recherche"),
    platform: Optional[str] = Query(None, description="Filtrer par plateforme"),
    min_score: Optional[float] = Query(None, ge=0, description="Score minimum"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Recherche de posts avec PostgreSQL"""
    # Recherche PostgreSQL
    query = db.query(Post)
    
    if platform:
        query = query.join(Platform).filter(Platform.name == platform)
    
    if min_score is not None:
        query = query.filter(Post.score >= min_score)
    
    # Recherche basique dans caption
    query = query.filter(Post.caption.ilike(f"%{q}%"))
    
    posts = query.order_by(Post.score_trend.desc(), Post.posted_at.desc()).offset(offset).limit(limit).all()
    return posts

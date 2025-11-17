# hashtags/hashtags_endpoints.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Optional
from db.base import get_db
from db.models import Hashtag, Platform, User
from auth_unified.auth_endpoints import get_current_user
from .schemas import HashtagCreate, HashtagResponse, HashtagUpdate

hashtags_router = APIRouter(prefix="/api/v1/hashtags", tags=["hashtags"])

@hashtags_router.get("/", response_model=List[HashtagResponse])
def get_hashtags(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    platform: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer les hashtags avec filtres"""
    query = db.query(Hashtag)
    
    if platform:
        query = query.join(Platform).filter(Platform.name == platform)
    
    hashtags = query.offset(skip).limit(limit).all()
    return hashtags

@hashtags_router.get("/{hashtag_id}", response_model=HashtagResponse)
def get_hashtag(
    hashtag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer un hashtag par ID"""
    hashtag = db.query(Hashtag).filter(Hashtag.id == hashtag_id).first()
    if not hashtag:
        raise HTTPException(status_code=404, detail="Hashtag non trouvé")
    return hashtag

@hashtags_router.post("/", response_model=HashtagResponse)
def create_hashtag(
    hashtag_in: HashtagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un nouveau hashtag"""
    # Vérifier que la plateforme existe
    platform = db.query(Platform).filter(Platform.id == hashtag_in.platform_id).first()
    if not platform:
        raise HTTPException(status_code=400, detail="Plateforme non trouvée")
    
    # Vérifier que le hashtag n'existe pas déjà
    existing = db.query(Hashtag).filter(
        Hashtag.name == hashtag_in.name,
        Hashtag.platform_id == hashtag_in.platform_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Hashtag déjà existant")
    
    hashtag = Hashtag(**hashtag_in.dict())
    db.add(hashtag)
    db.commit()
    db.refresh(hashtag)
    return hashtag

@hashtags_router.put("/{hashtag_id}", response_model=HashtagResponse)
def update_hashtag(
    hashtag_id: int,
    hashtag_in: HashtagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour un hashtag"""
    hashtag = db.query(Hashtag).filter(Hashtag.id == hashtag_id).first()
    if not hashtag:
        raise HTTPException(status_code=404, detail="Hashtag non trouvé")
    
    update_data = hashtag_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(hashtag, field, value)
    
    db.commit()
    db.refresh(hashtag)
    return hashtag

@hashtags_router.delete("/{hashtag_id}")
def delete_hashtag(
    hashtag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer un hashtag"""
    hashtag = db.query(Hashtag).filter(Hashtag.id == hashtag_id).first()
    if not hashtag:
        raise HTTPException(status_code=404, detail="Hashtag non trouvé")
    
    db.delete(hashtag)
    db.commit()
    return {"message": "Hashtag supprimé"}

@hashtags_router.get("/stats/{hashtag_id}")
def get_hashtag_stats(
    hashtag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer les statistiques d'un hashtag"""
    hashtag = db.query(Hashtag).filter(Hashtag.id == hashtag_id).first()
    if not hashtag:
        raise HTTPException(status_code=404, detail="Hashtag non trouvé")
    
    # Utiliser la vue hashtags_with_stats
    result = db.execute(
        text("SELECT * FROM hashtags_with_stats WHERE id = :hashtag_id"),
        {"hashtag_id": hashtag_id}
    )
    stats = result.fetchone()
    
    if not stats:
        return {"message": "Aucune statistique disponible"}
    
    return {
        "id": stats[0],
        "name": stats[1],
        "platform": stats[2],
        "total_posts": stats[3],
        "avg_engagement": stats[4],
        "last_scraped": stats[5],
        "updated_at": stats[6]
    }

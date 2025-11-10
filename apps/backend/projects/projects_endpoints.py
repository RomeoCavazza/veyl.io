# projects/projects_endpoints.py
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List

from db.base import get_db
from db.models import Project, User, ProjectHashtag, ProjectCreator, Hashtag, Platform
from auth_unified.auth_endpoints import get_current_user
from projects.schemas import ProjectCreate, ProjectUpdate, ProjectResponse

logger = logging.getLogger(__name__)
projects_router = APIRouter(prefix="/api/v1/projects", tags=["projects"])

def serialize_project(project: Project, include_relations: bool = True) -> dict:
    """Sérialise un projet pour la réponse API"""
    result = {
        'id': project.id,
        'user_id': project.user_id,
        'name': project.name,
        'description': project.description,
        'status': project.status,
        'platforms': json.loads(project.platforms) if project.platforms else [],
        'scope_type': project.scope_type,
        'scope_query': project.scope_query,
        'creators_count': project.creators_count,
        'posts_count': project.posts_count,
        'signals_count': project.signals_count,
        'last_run_at': project.last_run_at.isoformat() if project.last_run_at else None,
        'last_signal_at': project.last_signal_at.isoformat() if project.last_signal_at else None,
        'created_at': project.created_at.isoformat() if project.created_at else None,
        'updated_at': project.updated_at.isoformat() if project.updated_at else None,
    }
    
    if include_relations:
        # Charger les hashtags liés
        project_hashtags = project.hashtags if hasattr(project, 'hashtags') else []
        result['hashtags'] = [
            {'id': h.id, 'name': h.name, 'platform_id': h.platform_id}
            for h in project_hashtags
        ] if project_hashtags else []
        
        # Charger les créateurs liés
        project_creators = project.creators if hasattr(project, 'creators') else []
        result['creators'] = [
            {'id': c.id, 'creator_username': c.creator_username, 'platform_id': c.platform_id}
            for c in project_creators
        ] if project_creators else []
    
    return result

@projects_router.get("", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste tous les projets de l'utilisateur"""
    try:
        projects = (
            db.query(Project)
            .filter(Project.user_id == current_user.id)
            .all()
        )
        return [serialize_project(p, include_relations=False) for p in projects]
    except Exception as exc:
        logger.exception("Erreur lors de la récupération des projets pour l'utilisateur %s", current_user.id)
        raise HTTPException(status_code=500, detail=f"Impossible de lister les projets: {exc}") from exc

@projects_router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer un projet spécifique"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return serialize_project(project)

@projects_router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un nouveau projet avec hashtags et créateurs"""
    try:
        # Sécuriser la présence des colonnes scope_* (cas legacy où la migration n'a pas été appliquée)
        db.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS scope_type VARCHAR(50);"))
        db.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS scope_query TEXT;"))

        # Compatibilité Pydantic v1 et v2
        if hasattr(project_in, 'model_dump'):
            project_data = project_in.model_dump(exclude={'hashtag_names', 'creator_usernames'})
        else:
            project_data = project_in.dict(exclude={'hashtag_names', 'creator_usernames'})
        
        # Sérialiser platforms en JSON
        project_data['platforms'] = json.dumps(project_data.get('platforms', []))
        
        # Créer le projet
        project = Project(
            user_id=current_user.id,
            **project_data
        )
        db.add(project)
        db.flush()  # Pour obtenir l'ID du projet
        
        # Ajouter les hashtags (créer ou réutiliser ceux existants)
        hashtag_names = project_in.hashtag_names or []
        creators_count = 0
        for hashtag_name in hashtag_names:
            # Normaliser (supprimer # si présent)
            normalized_name = hashtag_name.replace('#', '').strip()
            
            # Trouver ou créer le hashtag pour chaque plateforme du projet
            platforms = project_in.platforms or []
            for platform_name in platforms:
                # Trouver la plateforme
                platform = db.query(Platform).filter(Platform.name == platform_name.lower()).first()
                if not platform:
                    continue
                
                # Chercher le hashtag existant
                hashtag = db.query(Hashtag).filter(
                    Hashtag.name == normalized_name,
                    Hashtag.platform_id == platform.id
                ).first()
                
                # Créer si n'existe pas
                if not hashtag:
                    hashtag = Hashtag(
                        name=normalized_name,
                        platform_id=platform.id
                    )
                    db.add(hashtag)
                    db.flush()
                
                # Créer la liaison (éviter doublons)
                existing_link = db.query(ProjectHashtag).filter(
                    ProjectHashtag.project_id == project.id,
                    ProjectHashtag.hashtag_id == hashtag.id
                ).first()
                
                if not existing_link:
                    project_hashtag = ProjectHashtag(
                        project_id=project.id,
                        hashtag_id=hashtag.id
                    )
                    db.add(project_hashtag)
        
        # Ajouter les créateurs
        creator_usernames = project_in.creator_usernames or []
        for creator_username in creator_usernames:
            # Normaliser (supprimer @ si présent)
            normalized_username = creator_username.replace('@', '').strip()
            
            # Trouver la plateforme
            platforms = project_in.platforms or ['instagram']  # Default Instagram
            for platform_name in platforms:
                platform = db.query(Platform).filter(Platform.name == platform_name.lower()).first()
                if not platform:
                    continue
                
                # Créer la liaison (éviter doublons)
                existing_creator = db.query(ProjectCreator).filter(
                    ProjectCreator.project_id == project.id,
                    ProjectCreator.platform_id == platform.id,
                    ProjectCreator.creator_username == normalized_username
                ).first()
                
                if not existing_creator:
                    project_creator = ProjectCreator(
                        project_id=project.id,
                        creator_username=normalized_username,
                        platform_id=platform.id
                    )
                    db.add(project_creator)
                    creators_count += 1
        
        # Mettre à jour les compteurs
        project.creators_count = creators_count
        
        db.commit()
        db.refresh(project)
        return serialize_project(project)
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("Erreur lors de la création du projet pour l'utilisateur %s", current_user.id)
        raise HTTPException(status_code=500, detail=f"Création du projet impossible: {exc}") from exc

@projects_router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour un projet"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Compatibilité Pydantic v1 et v2
    if hasattr(project_in, 'model_dump'):
        update_data = project_in.model_dump(exclude_unset=True, exclude={'hashtag_names', 'creator_usernames'})
    else:
        update_data = project_in.dict(exclude_unset=True, exclude={'hashtag_names', 'creator_usernames'})
    
    # Sérialiser platforms en JSON si présent
    if 'platforms' in update_data:
        update_data['platforms'] = json.dumps(update_data['platforms'])
    
    # Mettre à jour les champs du projet
    for field, value in update_data.items():
        setattr(project, field, value)
    
    # Gérer les hashtags si fournis
    if project_in.hashtag_names is not None:
        # Supprimer les anciennes liaisons
        db.query(ProjectHashtag).filter(ProjectHashtag.project_id == project.id).delete()
        
        # Ajouter les nouveaux hashtags (même logique que create)
        hashtag_names = project_in.hashtag_names or []
        platforms = project_in.platforms or json.loads(project.platforms) if project.platforms else []
        for hashtag_name in hashtag_names:
            normalized_name = hashtag_name.replace('#', '').strip()
            for platform_name in platforms:
                platform = db.query(Platform).filter(Platform.name == platform_name.lower()).first()
                if not platform:
                    continue
                hashtag = db.query(Hashtag).filter(
                    Hashtag.name == normalized_name,
                    Hashtag.platform_id == platform.id
                ).first()
                if not hashtag:
                    hashtag = Hashtag(name=normalized_name, platform_id=platform.id)
                    db.add(hashtag)
                    db.flush()
                project_hashtag = ProjectHashtag(project_id=project.id, hashtag_id=hashtag.id)
                db.add(project_hashtag)
    
    # Gérer les créateurs si fournis
    if project_in.creator_usernames is not None:
        # Supprimer les anciennes liaisons
        db.query(ProjectCreator).filter(ProjectCreator.project_id == project.id).delete()
        
        # Ajouter les nouveaux créateurs
        creator_usernames = project_in.creator_usernames or []
        platforms = project_in.platforms or json.loads(project.platforms) if project.platforms else ['instagram']
        creators_count = 0
        for creator_username in creator_usernames:
            normalized_username = creator_username.replace('@', '').strip()
            for platform_name in platforms:
                platform = db.query(Platform).filter(Platform.name == platform_name.lower()).first()
                if not platform:
                    continue
                project_creator = ProjectCreator(
                    project_id=project.id,
                    creator_username=normalized_username,
                    platform_id=platform.id
                )
                db.add(project_creator)
                creators_count += 1
        project.creators_count = creators_count
    
    db.commit()
    db.refresh(project)
    return serialize_project(project)

@projects_router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer un projet"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return None


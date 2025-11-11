# projects/projects_endpoints.py
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Set
from uuid import UUID

from db.base import get_db
from db.models import (
    Project,
    User,
    ProjectHashtag,
    ProjectCreator,
    Hashtag,
    Platform,
    Post,
    PostHashtag,
)
from auth_unified.auth_endpoints import get_current_user
from projects.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectCreatorCreate,
    ProjectHashtagCreate,
    ProjectPostResponse,
)

logger = logging.getLogger(__name__)
projects_router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


def _normalize_creator(value: str) -> str:
    return value.strip().lstrip("@").lower()


def _normalize_hashtag(value: str) -> str:
    return value.strip().lstrip("#").lower()


def _ensure_platform(db: Session, name: Optional[str]) -> Platform:
    normalized = (name or "").strip().lower()
    if not normalized:
        raise HTTPException(status_code=400, detail="Platform invalide")
    platform = db.query(Platform).filter(Platform.name == normalized).first()
    if not platform:
        platform = Platform(name=normalized)
        db.add(platform)
        db.flush()
    return platform


def _get_project_or_404(db: Session, current_user: User, project_id: str) -> Project:
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Project ID invalide")
    project = (
        db.query(Project)
        .filter(Project.id == project_uuid, Project.user_id == current_user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _collect_project_posts(
    db: Session,
    project: Project,
    limit: Optional[int] = None,
) -> List[Post]:
    post_map: Dict[str, Post] = {}

    creator_links = (
        db.query(ProjectCreator)
        .filter(ProjectCreator.project_id == project.id)
        .all()
    )
    usernames = [link.creator_username for link in creator_links]
    if usernames:
        query = (
            db.query(Post)
            .filter(Post.author.in_(usernames))
            .order_by(Post.posted_at.desc().nullslast(), Post.fetched_at.desc().nullslast())
        )
        if limit:
            query = query.limit(limit)
        for post in query.all():
            post_map[post.id] = post

    hashtag_links = (
        db.query(ProjectHashtag)
        .filter(ProjectHashtag.project_id == project.id)
        .all()
    )
    hashtag_ids = [link.hashtag_id for link in hashtag_links]
    if hashtag_ids:
        hashtag_query = (
            db.query(Post)
            .join(PostHashtag, PostHashtag.post_id == Post.id)
            .filter(PostHashtag.hashtag_id.in_(hashtag_ids))
            .order_by(Post.posted_at.desc().nullslast(), Post.fetched_at.desc().nullslast())
        )
        if limit:
            hashtag_query = hashtag_query.limit(limit)
        for post in hashtag_query.all():
            post_map[post.id] = post

    posts = list(post_map.values())

    def _sort_key(post: Post) -> float:
        for candidate in (post.posted_at, post.fetched_at):
            if candidate:
                if candidate.tzinfo:
                    return candidate.timestamp()
                return candidate.replace(tzinfo=timezone.utc).timestamp()
        return 0.0

    posts.sort(key=_sort_key, reverse=True)

    if limit:
        return posts[:limit]
    return posts


def _sync_project_metadata(db: Session, project: Project) -> None:
    creators = (
        db.query(ProjectCreator)
        .filter(ProjectCreator.project_id == project.id)
        .all()
    )

    hashtag_rows = (
        db.query(ProjectHashtag, Hashtag)
        .join(Hashtag, ProjectHashtag.hashtag_id == Hashtag.id)
        .filter(ProjectHashtag.project_id == project.id)
        .all()
    )

    platform_names: Set[str] = set()
    scope_parts: List[str] = []

    for creator in creators:
        scope_parts.append(f"@{creator.creator_username}")
        if creator.platform:
            platform_names.add(creator.platform.name)

    hashtag_count = 0
    for _, hashtag in hashtag_rows:
        hashtag_count += 1
        scope_parts.append(f"#{hashtag.name}")
        if hashtag.platform:
            platform_names.add(hashtag.platform.name)

    posts = _collect_project_posts(db, project)

    project.creators_count = len(creators)
    if hashtag_count and project.creators_count:
        project.scope_type = "both"
    elif hashtag_count:
        project.scope_type = "hashtags"
    elif project.creators_count:
        project.scope_type = "creators"
    else:
        project.scope_type = None

    project.scope_query = ", ".join(scope_parts) if scope_parts else None
    project.platforms = (
        json.dumps(sorted(platform_names)) if platform_names else json.dumps([])
    )
    project.posts_count = len(posts)


def _attach_creator(
    db: Session,
    project: Project,
    username: str,
    platform_name: str,
) -> ProjectCreator:
    normalized_username = _normalize_creator(username)
    if not normalized_username:
        raise HTTPException(status_code=400, detail="Creator username invalide")

    platform = _ensure_platform(db, platform_name)

    existing = (
        db.query(ProjectCreator)
        .filter(
            ProjectCreator.project_id == project.id,
            ProjectCreator.platform_id == platform.id,
            ProjectCreator.creator_username == normalized_username,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Creator already linked to project")

    creator = ProjectCreator(
        project_id=project.id,
        creator_username=normalized_username,
        platform_id=platform.id,
    )
    db.add(creator)
    return creator


def _attach_hashtag(
    db: Session,
    project: Project,
    hashtag_value: str,
    platform_name: str,
) -> ProjectHashtag:
    normalized_name = _normalize_hashtag(hashtag_value)
    if not normalized_name:
        raise HTTPException(status_code=400, detail="Hashtag invalide")

    platform = _ensure_platform(db, platform_name)

    hashtag = (
        db.query(Hashtag)
        .filter(Hashtag.name == normalized_name, Hashtag.platform_id == platform.id)
        .first()
    )
    if not hashtag:
        hashtag = Hashtag(name=normalized_name, platform_id=platform.id)
        db.add(hashtag)
        db.flush()

    existing = (
        db.query(ProjectHashtag)
        .filter(
            ProjectHashtag.project_id == project.id,
            ProjectHashtag.hashtag_id == hashtag.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Hashtag already linked to project")

    project_hashtag = ProjectHashtag(project_id=project.id, hashtag_id=hashtag.id)
    db.add(project_hashtag)
    
    # 🔥 AUTO-LINK: Lier automatiquement les posts existants qui ont ce hashtag
    # Chercher les posts qui contiennent ce hashtag dans leur caption
    posts_with_hashtag = (
        db.query(Post)
        .filter(
            Post.platform_id == platform.id,
            Post.caption.ilike(f'%#{normalized_name}%')
        )
        .limit(50)  # Limiter à 50 posts pour éviter la surcharge
        .all()
    )
    
    linked_count = 0
    for post in posts_with_hashtag:
        # Vérifier si le lien existe déjà
        existing_link = (
            db.query(PostHashtag)
            .filter(
                PostHashtag.post_id == post.id,
                PostHashtag.hashtag_id == hashtag.id
            )
            .first()
        )
        if not existing_link:
            post_hashtag_link = PostHashtag(
                post_id=post.id,
                hashtag_id=hashtag.id
            )
            db.add(post_hashtag_link)
            linked_count += 1
    
    if linked_count > 0:
        logger.info(f"✅ Auto-linked {linked_count} posts to #{normalized_name}")
    
    return project_hashtag


def serialize_project(project: Project, include_relations: bool = True) -> dict:
    """Sérialise un projet pour la réponse API"""
    result = {
        'id': str(project.id),
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
        project_hashtag_links = getattr(project, 'project_hashtag_links', [])
        result['hashtags'] = [
            {
                'link_id': link.id,
                'id': link.hashtag_id,
                'name': link.hashtag.name if link.hashtag else None,
                'platform_id': link.hashtag.platform_id if link.hashtag else None,
                'platform': link.hashtag.platform.name if link.hashtag and link.hashtag.platform else None,
                'added_at': link.added_at.isoformat() if link.added_at else None,
            }
            for link in project_hashtag_links
        ] if project_hashtag_links else []
        
        # Charger les créateurs liés
        project_creators = project.creators if hasattr(project, 'creators') else []
        result['creators'] = [
            {
                'id': c.id,
                'creator_username': c.creator_username,
                'platform_id': c.platform_id,
                'platform': c.platform.name if c.platform else None,
                'added_at': c.added_at.isoformat() if c.added_at else None,
            }
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
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer un projet spécifique"""
    project = _get_project_or_404(db, current_user, project_id)
    return serialize_project(project)

@projects_router.get("/{project_id}/posts", response_model=List[ProjectPostResponse])
def list_project_posts(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retourne les posts associés au projet (via ses créateurs)."""
    project = _get_project_or_404(db, current_user, project_id)

    posts = _collect_project_posts(db, project, limit=60)
    if not posts:
        return []

    results: List[ProjectPostResponse] = []
    for post in posts:
        metrics: dict = {}
        if post.metrics:
            try:
                metrics = json.loads(post.metrics)
            except (TypeError, ValueError):
                metrics = {}
        permalink = None
        if post.external_id:
            permalink = (
                post.external_id
                if post.external_id.startswith('http')
                else f"https://www.instagram.com/p/{post.external_id.strip('/')}/"
            )
        elif post.api_payload:
            try:
                payload_data = json.loads(post.api_payload)
                media_details = payload_data.get('media_details') or {}
                permalink_candidate = (
                    media_details.get('permalink')
                    or payload_data.get('url')
                    or payload_data.get('author_url')
                )
                if isinstance(permalink_candidate, str) and permalink_candidate.startswith('http'):
                    permalink = permalink_candidate
            except (TypeError, ValueError):
                permalink = None

        results.append(ProjectPostResponse(
            id=post.id,
            author=post.author,
            caption=post.caption,
            media_url=post.media_url,
            permalink=permalink,
            posted_at=post.posted_at,
            platform=post.platform.name if post.platform else None,
            like_count=metrics.get('like_count') or metrics.get('likes') or 0,
            comment_count=metrics.get('comment_count') or metrics.get('comments_count') or 0,
            score_trend=post.score_trend,
        ))

    return results

@projects_router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un nouveau projet (peut être vide)."""
    try:
        # Sécuriser la présence des colonnes (compat legacy)
        db.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS scope_type VARCHAR(50);"))
        db.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS scope_query TEXT;"))
        db.execute(
            text(
                """
                DO $$
                DECLARE
                    column_udt text;
                BEGIN
                    SELECT udt_name INTO column_udt
                    FROM information_schema.columns
                    WHERE table_name = 'projects'
                      AND column_name = 'platforms';

                    IF column_udt IS NOT NULL AND column_udt LIKE '\\_%' THEN
                        EXECUTE 'ALTER TABLE projects ALTER COLUMN platforms DROP DEFAULT;';

                        IF column_udt = '_int8' THEN
                            EXECUTE 'ALTER TABLE projects
                                     ALTER COLUMN platforms
                                     TYPE text
                                     USING to_json(COALESCE(platforms::text[], ARRAY[]::text[]))::text;';
                        ELSE
                            EXECUTE 'ALTER TABLE projects
                                     ALTER COLUMN platforms
                                     TYPE text
                                     USING to_json(COALESCE(platforms, ARRAY[]::text[]))::text;';
                        END IF;

                        EXECUTE 'ALTER TABLE projects ALTER COLUMN platforms SET DEFAULT ''[]'';';
                    END IF;
                END $$;
                """
            )
        )

        db.execute(
            text(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'hashtags' AND column_name = 'last_scraped'
                    ) THEN
                        EXECUTE 'ALTER TABLE hashtags ADD COLUMN last_scraped TIMESTAMP;';
                    END IF;

                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'hashtags' AND column_name = 'updated_at'
                    ) THEN
                        EXECUTE 'ALTER TABLE hashtags ADD COLUMN updated_at TIMESTAMP;';
                    END IF;
                END $$;
                """
            )
        )

        if hasattr(project_in, "model_dump"):
            project_data = project_in.model_dump(exclude={"hashtag_names", "creator_usernames"})
        else:
            project_data = project_in.dict(exclude={"hashtag_names", "creator_usernames"})

        name = (project_data.get("name") or "Untitled project").strip()
        project_data["name"] = name or "Untitled project"

        status_value = (project_data.get("status") or "draft").strip()
        project_data["status"] = status_value or "draft"

        project_data["platforms"] = json.dumps(project_data.get("platforms") or [])
        project_data["scope_type"] = None
        project_data["scope_query"] = None
        project_data.setdefault("creators_count", 0)
        project_data.setdefault("posts_count", 0)
        project_data.setdefault("signals_count", 0)

        project = Project(
            user_id=current_user.id,
            **project_data,
        )
        db.add(project)
        db.flush()

        candidate_platforms = project_in.platforms or []
        if not candidate_platforms and (project_in.hashtag_names or project_in.creator_usernames):
            candidate_platforms = ["instagram"]

        for hashtag_name in project_in.hashtag_names or []:
            for platform_name in candidate_platforms or ["instagram"]:
                try:
                    _attach_hashtag(db, project, hashtag_name, platform_name)
                except HTTPException as err:
                    if err.status_code != 409:
                        raise

        for creator_username in project_in.creator_usernames or []:
            platform_name = candidate_platforms[0] if candidate_platforms else "instagram"
            try:
                _attach_creator(db, project, creator_username, platform_name)
            except HTTPException as err:
                if err.status_code != 409:
                    raise

        _sync_project_metadata(db, project)
        db.commit()
        db.refresh(project)
        return serialize_project(project)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("Erreur lors de la création du projet pour l'utilisateur %s", current_user.id)
        raise HTTPException(status_code=500, detail=f"Création du projet impossible: {exc}") from exc

@projects_router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour un projet"""
    project = _get_project_or_404(db, current_user, project_id)

    try:
        if hasattr(project_in, "model_dump"):
            update_data = project_in.model_dump(exclude_unset=True, exclude={"hashtag_names", "creator_usernames"})
        else:
            update_data = project_in.dict(exclude_unset=True, exclude={"hashtag_names", "creator_usernames"})

        if "name" in update_data:
            name = (update_data["name"] or "").strip()
            update_data["name"] = name or "Untitled project"

        if "status" in update_data:
            status_value = (update_data["status"] or "").strip()
            update_data["status"] = status_value or project.status or "draft"

        if "platforms" in update_data:
            update_data["platforms"] = json.dumps(update_data["platforms"] or [])

        for field, value in update_data.items():
            setattr(project, field, value)

        if project_in.hashtag_names is not None:
            db.query(ProjectHashtag).filter(ProjectHashtag.project_id == project.id).delete()
            platforms = project_in.platforms or json.loads(project.platforms) if project.platforms else ["instagram"]
            for hashtag_name in project_in.hashtag_names or []:
                for platform_name in platforms:
                    try:
                        _attach_hashtag(db, project, hashtag_name, platform_name)
                    except HTTPException as err:
                        if err.status_code != 409:
                            raise

        if project_in.creator_usernames is not None:
            db.query(ProjectCreator).filter(ProjectCreator.project_id == project.id).delete()
            platforms = project_in.platforms or json.loads(project.platforms) if project.platforms else ["instagram"]
            for creator_username in project_in.creator_usernames or []:
                platform_name = platforms[0] if platforms else "instagram"
                try:
                    _attach_creator(db, project, creator_username, platform_name)
                except HTTPException as err:
                    if err.status_code != 409:
                        raise

        _sync_project_metadata(db, project)
        db.commit()
        db.refresh(project)
        return serialize_project(project)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("Erreur lors de la mise à jour du projet %s", project_id)
        raise HTTPException(status_code=500, detail=f"Mise à jour du projet impossible: {exc}") from exc

@projects_router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer un projet"""
    project = _get_project_or_404(db, current_user, project_id)
    db.delete(project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@projects_router.get("/creators/search")
def search_creators(
    q: str = Query(..., min_length=1, description="Search query for creator username"),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🔍 Autocomplete: Chercher des creators dans la DB pour l'autocomplétion."""
    # Chercher dans la table posts les auteurs uniques qui matchent la query
    results = (
        db.query(Post.author)
        .filter(Post.author.ilike(f'%{q}%'))
        .distinct()
        .limit(limit)
        .all()
    )
    
    creators = [{"username": r[0]} for r in results if r[0]]
    return {"creators": creators, "count": len(creators)}


@projects_router.post("/{project_id}/creators", response_model=ProjectResponse)
def add_project_creator(
    project_id: str,
    payload: ProjectCreatorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ajouter un créateur au projet."""
    project = _get_project_or_404(db, current_user, project_id)

    try:
        _attach_creator(db, project, payload.username, payload.platform)
        _sync_project_metadata(db, project)
        db.commit()
        db.refresh(project)
        return serialize_project(project)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("Erreur lors de l'ajout d'un créateur au projet %s", project_id)
        raise HTTPException(status_code=500, detail=f"Ajout du créateur impossible: {exc}") from exc


@projects_router.delete("/{project_id}/creators/{creator_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_project_creator(
    project_id: str,
    creator_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer un créateur du projet."""
    project = _get_project_or_404(db, current_user, project_id)

    creator = (
        db.query(ProjectCreator)
        .filter(ProjectCreator.project_id == project.id, ProjectCreator.id == creator_id)
        .first()
    )
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")

    db.delete(creator)
    db.flush()
    _sync_project_metadata(db, project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@projects_router.post("/{project_id}/hashtags", response_model=ProjectResponse)
def add_project_hashtag(
    project_id: str,
    payload: ProjectHashtagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ajouter un hashtag au projet."""
    project = _get_project_or_404(db, current_user, project_id)

    try:
        _attach_hashtag(db, project, payload.hashtag, payload.platform)
        _sync_project_metadata(db, project)
        db.commit()
        db.refresh(project)
        return serialize_project(project)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("Erreur lors de l'ajout d'un hashtag au projet %s", project_id)
        raise HTTPException(status_code=500, detail=f"Ajout du hashtag impossible: {exc}") from exc


@projects_router.delete("/{project_id}/hashtags/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_project_hashtag(
    project_id: str,
    link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer un hashtag du projet."""
    project = _get_project_or_404(db, current_user, project_id)

    project_hashtag = (
        db.query(ProjectHashtag)
        .filter(ProjectHashtag.project_id == project.id, ProjectHashtag.id == link_id)
        .first()
    )
    if not project_hashtag:
        raise HTTPException(status_code=404, detail="Hashtag not found")

    db.delete(project_hashtag)
    db.flush()
    _sync_project_metadata(db, project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


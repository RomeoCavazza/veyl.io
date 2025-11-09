import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from auth_unified.auth_endpoints import get_current_user
from core.config import settings
from db.base import get_db
from db.models import Post, Platform, User
from services.meta_client import call_meta

router = APIRouter(prefix="/api/v1/meta", tags=["meta"])


def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    ts = value.replace("Z", "+00:00")
    if ts.endswith("+0000"):
        ts = ts[:-5] + "+00:00"
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def _ensure_platform(db: Session, name: str) -> Platform:
    platform = db.query(Platform).filter(Platform.name == name).first()
    if not platform:
        platform = Platform(name=name)
        db.add(platform)
        db.flush()
    return platform


def _upsert_post(
    db: Session,
    platform_name: str,
    external_id: str,
    payload: dict,
    source: str,
    defaults: dict,
) -> Post:
    platform = _ensure_platform(db, platform_name)
    post = (
        db.query(Post)
        .filter(or_(Post.id == external_id, Post.external_id == external_id))
        .first()
    )

    if not post:
        post = Post(
            id=external_id,
            external_id=external_id,
            platform_id=platform.id,
            source=source,
        )
        db.add(post)

    post.platform_id = platform.id
    post.external_id = external_id
    post.source = source
    for key, value in defaults.items():
        if value is not None:
            setattr(post, key, value)

    post.api_payload = json.dumps(payload)
    post.last_fetch_at = datetime.utcnow()
    return post


@router.get("/oembed")
async def get_oembed(
    url: str = Query(..., description="URL publique IG/FB à embarquer"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not url:
        raise HTTPException(status_code=400, detail="url parameter required")

    payload = await call_meta(
        method="GET",
        endpoint="v21.0/instagram_oembed",
        params={"url": url, "maxwidth": 540},
    )

    media_id = payload.get("media_id") or url
    platform_name = (payload.get("provider_name") or "instagram").lower()

    defaults = {
        "author": payload.get("author_name"),
        "caption": payload.get("title"),
        "media_url": payload.get("thumbnail_url"),
        "fetched_at": datetime.utcnow(),
    }

    _upsert_post(
        db=db,
        platform_name=platform_name,
        external_id=str(media_id),
        payload=payload,
        source="meta_oembed",
        defaults=defaults,
    )
    db.commit()
    return payload


@router.get("/ig-hashtag")
async def get_instagram_hashtag_media(
    tag: str = Query(..., min_length=1),
    user_id: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ig_user_id = user_id or settings.IG_USER_ID
    if not ig_user_id:
        raise HTTPException(status_code=400, detail="IG_USER_ID required")

    search = await call_meta(
        method="GET",
        endpoint="v21.0/ig_hashtag_search",
        params={"user_id": ig_user_id, "q": tag},
    )
    data = search.get("data", [])
    if not data:
        return {"data": []}

    hashtag_id = data[0]["id"]
    media = await call_meta(
        method="GET",
        endpoint=f"v21.0/{hashtag_id}/recent_media",
        params={
            "user_id": ig_user_id,
            "fields": "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count",
            "limit": limit,
        },
    )

    for item in media.get("data", []):
        external_id = item.get("id")
        if not external_id:
            continue

        metrics = {
            "like_count": item.get("like_count"),
            "comment_count": item.get("comments_count"),
        }

        defaults = {
            "caption": item.get("caption"),
            "media_url": item.get("media_url"),
            "posted_at": _parse_timestamp(item.get("timestamp")),
            "metrics": json.dumps(metrics),
            "fetched_at": datetime.utcnow(),
        }

        _upsert_post(
            db=db,
            platform_name="instagram",
            external_id=str(external_id),
            payload=item,
            source="meta_hashtag",
            defaults=defaults,
        )

    db.commit()
    return media


@router.get("/page-public")
async def get_page_public_posts(
    page_id: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    posts = await call_meta(
        method="GET",
        endpoint=f"v21.0/{page_id}/posts",
        params={
            "fields": "id,message,permalink_url,created_time,full_picture",
            "limit": limit,
        },
    )

    for item in posts.get("data", []):
        external_id = item.get("id")
        if not external_id:
            continue

        defaults = {
            "caption": item.get("message"),
            "media_url": item.get("full_picture"),
            "posted_at": _parse_timestamp(item.get("created_time")),
            "metrics": json.dumps({"permalink_url": item.get("permalink_url")}),
            "fetched_at": datetime.utcnow(),
        }

        _upsert_post(
            db=db,
            platform_name="facebook",
            external_id=str(external_id),
            payload=item,
            source="meta_page_public",
            defaults=defaults,
        )

    db.commit()
    return posts


@router.get("/insights")
async def get_insights(
    resource_id: str = Query(..., description="IG Business ID ou Page ID"),
    platform: str = Query("instagram", pattern="^(instagram|facebook)$"),
    metrics: str = Query(..., description="Liste metrics Graph API"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    endpoint = f"v21.0/{resource_id}/insights"
    params = {"metric": metrics}
    if platform == "instagram":
        params["period"] = "day"

    insights = await call_meta(method="GET", endpoint=endpoint, params=params)

    defaults = {
        "caption": f"{platform} insights for {resource_id}",
        "metrics": json.dumps({"metrics": metrics.split(",")}),
        "fetched_at": datetime.utcnow(),
    }

    external_id = f"insights:{platform}:{resource_id}:{metrics}"

    _upsert_post(
        db=db,
        platform_name=platform,
        external_id=external_id,
        payload=insights,
        source="meta_insights",
        defaults=defaults,
    )

    db.commit()
    return insights



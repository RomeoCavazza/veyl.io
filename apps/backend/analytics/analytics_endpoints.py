# analytics/analytics_endpoints.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from db.base import get_db
from db.models import User
from auth_unified.auth_endpoints import get_current_user
from .schemas import TrendingPostResponse, HashtagStatsResponse

analytics_router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@analytics_router.get("/trending", response_model=List[TrendingPostResponse])
def get_trending_posts(
    platform: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer les posts les plus tendance"""
    if platform:
        # Utiliser la fonction PostgreSQL
        result = db.execute(f"SELECT * FROM get_trending_posts('{platform}', {limit})")
    else:
        result = db.execute(f"SELECT * FROM get_trending_posts(NULL, {limit})")
    
    posts = result.fetchall()
    return [
        TrendingPostResponse(
            post_id=post[0],
            author=post[1],
            caption=post[2],
            score=post[3],
            score_trend=post[4],
            posted_at=post[5]
        ) for post in posts
    ]

@analytics_router.get("/hashtags/stats", response_model=List[HashtagStatsResponse])
def get_hashtags_stats(
    platform: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer les statistiques des hashtags"""
    query = "SELECT * FROM hashtags_with_stats"
    params = []
    
    if platform:
        query += " WHERE platform = %s"
        params.append(platform)
    
    query += f" ORDER BY total_posts DESC LIMIT {limit}"
    
    result = db.execute(query, params)
    hashtags = result.fetchall()
    
    return [
        HashtagStatsResponse(
            id=hashtag[0],
            name=hashtag[1],
            platform=hashtag[2],
            total_posts=hashtag[3],
            avg_engagement=hashtag[4],
            last_scraped=hashtag[5],
            updated_at=hashtag[6]
        ) for hashtag in hashtags
    ]

@analytics_router.get("/posts/engagement")
def get_engagement_stats(
    platform: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer les statistiques d'engagement des posts"""
    query = """
        SELECT 
            COUNT(*) as total_posts,
            AVG(score) as avg_score,
            AVG(score_trend) as avg_trend_score,
            MAX(score) as max_score,
            MAX(score_trend) as max_trend_score
        FROM posts p
        JOIN platforms pl ON p.platform_id = pl.id
        WHERE p.posted_at > NOW() - INTERVAL '%s days'
    """
    
    params = [days]
    
    if platform:
        query += " AND pl.name = %s"
        params.append(platform)
    
    result = db.execute(query, params)
    stats = result.fetchone()
    
    return {
        "total_posts": stats[0],
        "avg_score": float(stats[1]) if stats[1] else 0,
        "avg_trend_score": float(stats[2]) if stats[2] else 0,
        "max_score": float(stats[3]) if stats[3] else 0,
        "max_trend_score": float(stats[4]) if stats[4] else 0,
        "period_days": days,
        "platform": platform or "all"
    }

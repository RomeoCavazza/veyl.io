# webhooks/webhooks_endpoints.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db.base import get_db
from db.models import OAuthAccount

webhooks_router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])

@webhooks_router.post("/facebook/deauthorize")
async def facebook_deauthorize(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Webhook Facebook pour gérer la déconnexion d'un utilisateur
    Appelé quand un utilisateur retire l'autorisation de l'application
    """
    try:
        # Récupérer les données JSON du body
        body = await request.json()
        user_id = body.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id manquant")
        
        # Trouver et supprimer les comptes OAuth Facebook/Instagram associés
        oauth_accounts = db.query(OAuthAccount).filter(
            OAuthAccount.provider_user_id == str(user_id),
            OAuthAccount.provider.in_(["facebook", "instagram"])
        ).all()
        
        deleted_count = 0
        for account in oauth_accounts:
            db.delete(account)
            deleted_count += 1
        
        db.commit()
        
        return {
            "message": "Comptes OAuth déconnectés",
            "user_id": user_id,
            "deleted_accounts": deleted_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la déconnexion: {str(e)}")

@webhooks_router.post("/facebook/data-deletion")
async def facebook_data_deletion(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Webhook Facebook pour gérer les demandes de suppression de données
    Appelé quand un utilisateur demande la suppression de ses données via Facebook
    """
    try:
        # Récupérer les données JSON du body
        body = await request.json()
        
        user_id = body.get("user_id")
        confirmation_code = body.get("confirmation_code")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id manquant")
        
        # Trouver et supprimer les comptes OAuth associés
        oauth_accounts = db.query(OAuthAccount).filter(
            OAuthAccount.provider_user_id == str(user_id),
            OAuthAccount.provider.in_(["facebook", "instagram"])
        ).all()
        
        deleted_count = 0
        for account in oauth_accounts:
            db.delete(account)
            deleted_count += 1
        
        db.commit()
        
        return {
            "url": f"https://veyl.io/data-deletion?confirmation_code={confirmation_code or 'N/A'}",
            "deletion_request_id": f"req_{user_id}",
            "message": "Demande de suppression de données traitée",
            "deleted_accounts": deleted_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")

@webhooks_router.get("/facebook/deauthorize")
async def facebook_deauthorize_get():
    """
    Endpoint GET pour vérification du webhook Facebook (appelé par Facebook lors de la configuration)
    """
    # Facebook peut appeler en GET pour vérifier que l'endpoint existe
    return {"status": "ok", "message": "Endpoint deauthorize configuré"}

@webhooks_router.get("/facebook/data-deletion")
async def facebook_data_deletion_get():
    """
    Endpoint GET pour vérification du webhook Facebook (appelé par Facebook lors de la configuration)
    """
    # Facebook peut appeler en GET pour vérifier que l'endpoint existe
    return {"status": "ok", "message": "Endpoint data-deletion configuré"}


# auth/auth_endpoints.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from db.base import get_db
from db.models import User
from .schemas import UserCreate, UserResponse, TokenResponse, LoginRequest
from .auth_service import AuthService

auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
auth_service = AuthService()

# Gérer les requêtes preflight CORS manuellement
@auth_router.options("/login")
@auth_router.options("/register")
def options_handler():
    """Gérer les requêtes preflight OPTIONS"""
    return Response(status_code=200)

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Obtenir l'utilisateur actuel depuis le token JWT"""
    from jose import JWTError, jwt
    from core.config import settings
    
    try:
        # Récupérer le token depuis l'header Authorization
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token manquant")
        
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(status_code=401, detail="Token invalide")
        
        # Supporter les UUID (utilisés depuis la correction de la BDD)
        from uuid import UUID
        try:
            user_id = UUID(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(status_code=401, detail="Token invalide: user_id invalide")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")
    return user

@auth_router.post("/register", response_model=TokenResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Inscription simple"""
    print(f"📝 Register request received: {user_in.email}")
    try:
        result = auth_service.register_user(user_in, db)
        print(f"✅ Register successful: {user_in.email}")
        return result
    except Exception as e:
        print(f"❌ Register error: {e}")
        raise

@auth_router.post("/login", response_model=TokenResponse)
def login(user_in: LoginRequest, db: Session = Depends(get_db)):
    """Connexion simple"""
    print(f"🔑 Login request received: {user_in.email}")
    try:
        result = auth_service.login_user(user_in, db)
        print(f"✅ Login successful: {user_in.email}")
        return result
    except Exception as e:
        print(f"❌ Login error: {e}")
        raise

@auth_router.get("/me", response_model=UserResponse)
def get_me(request: Request, db: Session = Depends(get_db)):
    """Profil utilisateur"""
    return get_current_user(request, db)

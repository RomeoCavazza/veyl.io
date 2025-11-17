# auth/auth_service.py
import logging
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from core.config import settings
from db.models import User
from .schemas import UserCreate, TokenResponse, LoginRequest

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Vérifier un mot de passe"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hasher un mot de passe"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Créer un token JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def register_user(self, user_in: UserCreate, db: Session) -> TokenResponse:
        """Inscrire un nouvel utilisateur"""
        try:
            logger.info(f"Register attempt: {user_in.email}")
            
            # Vérifier si l'email existe déjà
            existing_user = db.query(User).filter(User.email == user_in.email).first()
            if existing_user:
                logger.warning(f"Email already exists: {user_in.email}")
                raise HTTPException(status_code=400, detail="Email déjà utilisé")
            
            # Créer l'utilisateur
            hashed_password = self.get_password_hash(user_in.password)
            logger.debug("Password hashed")
            
            user = User(
                email=user_in.email,
                password_hash=hashed_password,
                name=user_in.name,
                role='user'
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"User created: {user.id}")
            
            # Créer le token
            access_token = self.create_access_token(data={"sub": str(user.id)})
            logger.debug("Token created")
            
            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user=user
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"ERROR in register_user: {type(e).__name__}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Erreur création utilisateur: {str(e)}")
    
    def login_user(self, user_in, db: Session) -> TokenResponse:
        """Connecter un utilisateur"""
        user = db.query(User).filter(User.email == user_in.email).first()
        if not user or not self.verify_password(user_in.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
        
        # Créer le token
        access_token = self.create_access_token(data={"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user
        )

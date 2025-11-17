# auth_unified/schemas.py
# Schémas Pydantic pour l'authentification

from pydantic import BaseModel, EmailStr, validator, Field  # type: ignore
from datetime import datetime
from typing import Optional
from uuid import UUID
import re

class UserCreate(BaseModel):
    """Schéma pour la création d'utilisateur - VALIDATION RELÂCHÉE POUR DEV"""
    email: EmailStr = Field(..., description="Email valide requis")
    password: str = Field(..., min_length=6, max_length=128, description="Mot de passe (min 6 caractères)")
    name: str = Field(..., min_length=1, max_length=100, description="Nom (min 1 caractère)")
    
    @validator('password')
    def validate_password(cls, v):
        """Validation minimale du mot de passe - RELÂCHÉE POUR DEV"""
        # En production, réactiver les validations strictes
        if len(v) < 6:
            raise ValueError('Le mot de passe doit contenir au moins 6 caractères')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """Validation minimal du nom"""
        if len(v.strip()) < 1:
            raise ValueError('Le nom ne peut pas être vide')
        return v.strip()

class UserResponse(BaseModel):
    """Schéma pour la réponse utilisateur"""
    id: UUID
    email: str
    name: Optional[str]
    role: str
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    """Schéma pour la connexion - sans validation stricte"""
    email: EmailStr = Field(..., description="Email valide requis")
    password: str = Field(..., min_length=6, description="Mot de passe (min 6 caractères)")

class TokenResponse(BaseModel):
    """Schéma pour la réponse de token"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
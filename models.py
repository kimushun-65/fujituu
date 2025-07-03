from pydantic import BaseModel
from typing import Optional, Dict, Any
import re


class UserSignupRequest(BaseModel):
    user_id: str
    password: str
    
    def validate_user_id(self):
        # ユーザーIDは英数字とアンダースコアのみ許可
        if not re.match(r'^[a-zA-Z0-9_]+$', self.user_id):
            raise ValueError("user_id must contain only alphanumeric characters and underscores")
    
    def validate_password(self):
        # パスワードは無効な文字を含んでいるかチェック
        if not re.match(r'^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?`~]+$', self.password):
            raise ValueError("password contains invalid characters")


class UserUpdateRequest(BaseModel):
    nickname: Optional[str] = None
    comment: Optional[str] = None
    
    def validate_nickname(self):
        # ニックネームに無効な文字が含まれているかチェック
        if self.nickname and not re.match(r'^[^\x00-\x1F\x7F]+$', self.nickname):
            raise ValueError("nickname contains invalid characters")
    
    def validate_comment(self):
        # コメントに無効な文字が含まれているかチェック
        if self.comment and not re.match(r'^[^\x00-\x1F\x7F]+$', self.comment):
            raise ValueError("comment contains invalid characters")


class UserResponse(BaseModel):
    user_id: str
    nickname: Optional[str] = None
    comment: Optional[str] = None


class UserDetailResponse(BaseModel):
    message: str
    user: UserResponse


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    message: str
    cause: Optional[str] = None


# インメモリデータベースのシミュレーション
users_db: Dict[str, Dict[str, Any]] = {}
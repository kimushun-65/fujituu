from fastapi import FastAPI, Header, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from models import (
    UserSignupRequest, UserUpdateRequest, UserResponse, 
    UserDetailResponse, MessageResponse, users_db
)
from auth import hash_password, verify_password, decode_basic_auth
import re

# テスト用アカウントを事前作成
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    test_password = "Test-"
    hashed_password = hash_password(test_password)
    users_db["Test-"] = {
        "user_id": "Test-",
        "password": hashed_password,
        "nickname": "Test-",
        "comment": "テスト用アカウント"
    }
    yield
    # Shutdown（特に何もしない）

app = FastAPI(title="User Management API", version="1.0.0", lifespan=lifespan)
security = HTTPBasic()

# CORS設定を追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 422エラーを400エラーに変換するハンドラー
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"message": "Account creation failed", "cause": "Required user_id and password"}
    )


@app.post("/signup", status_code=200, response_model=UserDetailResponse)
async def signup(request: UserSignupRequest):
    try:
        # ユーザーIDのフォーマットを検証
        if not re.match(r'^[a-zA-Z0-9_]+$', request.user_id):
            return JSONResponse(
                status_code=400,
                content={"message": "Account creation failed", "cause": "Incorrect character pattern"}
            )
        
        # パスワードのフォーマットを検証
        if not re.match(r'^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?`~]+$', request.password):
            return JSONResponse(
                status_code=400,
                content={"message": "Account creation failed", "cause": "Incorrect character pattern"}
            )
        
        # ユーザーIDの長さを検証
        if len(request.user_id) < 6 or len(request.user_id) > 20:
            return JSONResponse(
                status_code=400,
                content={"message": "Account creation failed", "cause": "Input length is incorrect"}
            )
        
        # パスワードの長さを検証
        if len(request.password) < 8 or len(request.password) > 20:
            return JSONResponse(
                status_code=400,
                content={"message": "Account creation failed", "cause": "Input length is incorrect"}
            )
        
        # ユーザーIDとパスワードが提供されているかチェック
        if not request.user_id or not request.password:
            return JSONResponse(
                status_code=400,
                content={"message": "Account creation failed", "cause": "Required user_id and password"}
            )
        
        # ユーザーが既に存在するかチェック
        if request.user_id in users_db:
            return JSONResponse(
                status_code=400,
                content={"message": "Account creation failed", "cause": "Already same user_id is used"}
            )
        
        # パスワードをハッシュ化してユーザーを作成
        hashed_password = hash_password(request.password)
        users_db[request.user_id] = {
            "user_id": request.user_id,
            "password": hashed_password,
            "nickname": "TaroYamada",
            "comment": "僕は元気です"
        }
        
        return UserDetailResponse(
            message="Account successfully created",
            user=UserResponse(
                user_id=request.user_id,
                nickname="TaroYamada",
                comment="僕は元気です"
            )
        )
    
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"message": "Account creation failed", "cause": "Required user_id and password"}
        )


@app.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user(user_id: str, request: Request):
    # ユーザーが存在するかチェック
    if user_id not in users_db:
        return JSONResponse(
            status_code=404,
            content={"message": "No user found"}
        )
    
    user_data = users_db[user_id]
    
    # 認証ヘッダーがない場合、ニックネームが未設定の場合はユーザー情報を返す
    authorization = request.headers.get("authorization")
    if not authorization:
        return UserDetailResponse(
            message="User details by user_id",
            user=UserResponse(
                user_id=user_data["user_id"],
                nickname=user_data.get("nickname"),
                comment=user_data.get("comment")
            )
        )
    
    # 認証ヘッダーが提供された場合、それを検証
    try:
        auth_user_id, auth_password = decode_basic_auth(authorization)
        if auth_user_id != user_id or not verify_password(auth_password, user_data["password"]):
            return JSONResponse(
                status_code=401,
                content={"message": "Authentication failed"}
            )
    except ValueError:
        return JSONResponse(
            status_code=401,
            content={"message": "Authentication failed"}
        )
    
    return UserDetailResponse(
        message="User details by user_id",
        user=UserResponse(
            user_id=user_data["user_id"],
            nickname=user_data.get("nickname"),
            comment=user_data.get("comment")
        )
    )


@app.patch("/users/{user_id}", status_code=200, response_model=UserDetailResponse)
async def update_user(user_id: str, update_request: UserUpdateRequest, request: Request):
    # ユーザーが存在するかチェック
    if user_id not in users_db:
        return JSONResponse(
            status_code=404,
            content={"message": "No user found"}
        )
    
    # 認証ヘッダーが提供されているかチェック
    authorization = request.headers.get("authorization")
    if not authorization:
        return JSONResponse(
            status_code=401,
            content={"message": "Authentication failed"}
        )
    
    # 認証を検証
    try:
        auth_user_id, auth_password = decode_basic_auth(authorization)
        user_data = users_db[user_id]
        
        # 異なるユーザーIDの場合は403
        if auth_user_id != user_id:
            return JSONResponse(
                status_code=403,
                content={"message": "No permission for update"}
            )
        
        # パスワードが間違っている場合は401
        if not verify_password(auth_password, user_data["password"]):
            return JSONResponse(
                status_code=401,
                content={"message": "Authentication failed"}
            )
    except ValueError:
        return JSONResponse(
            status_code=401,
            content={"message": "Authentication failed"}
        )
    
    # 少なくとも1つのフィールドが提供されているかチェック
    if update_request.nickname is None and update_request.comment is None:
        return JSONResponse(
            status_code=400,
            content={"message": "User update failed", "cause": "Required nickname or comment"}
        )
    
    # ニックネームが提供されている場合は検証
    if update_request.nickname is not None:
        if len(update_request.nickname) > 30:
            return JSONResponse(
                status_code=400,
                content={"message": "User update failed", "cause": "Invalid nickname or comment"}
            )
        if not re.match(r'^[^\x00-\x1F\x7F]*$', update_request.nickname):
            return JSONResponse(
                status_code=400,
                content={"message": "User update failed", "cause": "Invalid nickname or comment"}
            )
    
    # コメントが提供されている場合は検証
    if update_request.comment is not None:
        if len(update_request.comment) > 100:
            return JSONResponse(
                status_code=400,
                content={"message": "User update failed", "cause": "Invalid nickname or comment"}
            )
        if not re.match(r'^[^\x00-\x1F\x7F]*$', update_request.comment):
            return JSONResponse(
                status_code=400,
                content={"message": "User update failed", "cause": "Invalid nickname or comment"}
            )
    
    # user_idやpasswordを更新しようとしているかチェック
    if hasattr(update_request, 'user_id') or hasattr(update_request, 'password'):
        return JSONResponse(
            status_code=400,
            content={"message": "User update failed", "cause": "Not updatable user_id and password"}
        )
    
    # ユーザーデータを更新
    if update_request.nickname is not None:
        users_db[user_id]["nickname"] = update_request.nickname
    if update_request.comment is not None:
        users_db[user_id]["comment"] = update_request.comment
    
    updated_user = users_db[user_id]
    
    return UserDetailResponse(
        message="User successfully updated",
        user=UserResponse(
            user_id=updated_user["user_id"],
            nickname=updated_user.get("nickname"),
            comment=updated_user.get("comment")
        )
    )


@app.post("/close", status_code=200, response_model=MessageResponse)
async def close_account(request: Request):
    # 認証ヘッダーが提供されているかチェック
    authorization = request.headers.get("authorization")
    if not authorization:
        return JSONResponse(
            status_code=401,
            content={"message": "Authentication failed"}
        )
    
    # 認証を検証
    try:
        auth_user_id, auth_password = decode_basic_auth(authorization)
        
        # ユーザーが存在するかチェック
        if auth_user_id not in users_db:
            return JSONResponse(
                status_code=401,
                content={"message": "Authentication failed"}
            )
        
        user_data = users_db[auth_user_id]
        
        if not verify_password(auth_password, user_data["password"]):
            return JSONResponse(
                status_code=401,
                content={"message": "Authentication failed"}
            )
    except ValueError:
        return JSONResponse(
            status_code=401,
            content={"message": "Authentication failed"}
        )
    
    # ユーザーアカウントを削除
    del users_db[auth_user_id]
    
    return MessageResponse(message="Account and user successfully removed")


if __name__ == "__main__":
    # サーバーを起動
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
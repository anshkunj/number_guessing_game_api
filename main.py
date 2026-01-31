from fastapi import FastAPI, Depends, HTTPException, WebSocket
from sqlalchemy.orm import Session

# Internal imports (package-style)
from .database import Base, engine, SessionLocal
from .models import User, Game
from .schemas import Register, LoginResponse, Guess, BullsCowsGuess
from .logic import generate_bulls_cows_number, check_bulls_cows
from .auth import (
    get_db,
    hash_password,
    verify_password,
    create_token,
    get_current_user,
    oauth2_scheme
)
from .chat import manager

import random

# ===== IMPORT HELPERS =====
from helpers import (
    create_repo,
    push_or_update_file,
    delete_file,
    delete_repo,
    rename_repo,
    rename_file,
    analyze_token_permissions,
    can_execute_action,
    edit_repo_description
)

app = FastAPI(title="Super Assistant – GitHub Automation")

# =========================================================
# 🔐 GLOBAL PERMISSION DECORATOR
# =========================================================
def require_permission(action_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request = kwargs.get("request") or args[0]
            token = request.github_token
            dry_run = getattr(request, "dry_run", False)

            scopes = analyze_token_permissions(token)

            if not can_execute_action(action_name, scopes):
                return {
                    "allowed": False,
                    "error": "INSUFFICIENT_PERMISSIONS",
                    "required_action": action_name,
                    "token_scopes": scopes
                }

            if dry_run:
                return {
                    "allowed": False,
                    "dry_run": True,
                    "message": f"DRY RUN: '{action_name}' will be executed",
                    "token_scopes": scopes
                }

            return func(*args, **kwargs)
        return wrapper
    return decorator


# =========================================================
# 📦 REQUEST MODELS
# =========================================================
class CreateRepoRequest(BaseModel):
    github_token: str
    repo_name: str
    description: Optional[str] = ""
    private: bool = False
    dry_run: bool = False


class FileItem(BaseModel):
    path: str
    content: str
    commit_message: str = "Add file"


class PushFilesRequest(BaseModel):
    github_token: str
    repo_name: str
    files: List[FileItem]
    dry_run: bool = False


class DeleteFileRequest(BaseModel):
    github_token: str
    repo_name: str
    path: str
    commit_message: str = "Delete file"
    dry_run: bool = False


class DeleteRepoRequest(BaseModel):
    github_token: str
    repo_name: str
    dry_run: bool = False


class RenameRepoRequest(BaseModel):
    github_token: str
    old_repo_name: str
    new_repo_name: str
    dry_run: bool = False


class EditDescriptionRequest(BaseModel):
    token: str
    username: str
    repo: str
    description: str


class RenameFileRequest(BaseModel):
    github_token: str
    repo_name: str
    old_path: str
    new_path: str
    commit_message: str = "Rename file"
    dry_run: bool = False


# =========================================================
# 👤 HELPER: GET USERNAME FROM TOKEN
# =========================================================
def get_username(token):
    headers = {"Authorization": f"token {token}"}
    r = requests.get("https://api.github.com/user", headers=headers)
    if r.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid GitHub token")
    return r.json()["login"]


# =========================================================
# 🚀 ENDPOINTS
# =========================================================

@app.post("/github/create-repo")
@require_permission("create_repo")
def create_repo_endpoint(request: CreateRepoRequest):
    username = get_username(request.github_token)
    return create_repo(
        request.github_token,
        request.repo_name,
        request.description,
        request.private
    )


@app.post("/github/push-files")
@require_permission("push_file")
def push_files_endpoint(request: PushFilesRequest):
    username = get_username(request.github_token)

    results = []
    for file in request.files:
        res = push_or_update_file(
            request.github_token,
            username,
            request.repo_name,
            file.path,
            file.content,
            file.commit_message
        )
        results.append({"path": file.path, "result": res})

    return {"status": "SUCCESS", "results": results}


@app.post("/github/delete-file")
@require_permission("delete_file")
def delete_file_endpoint(request: DeleteFileRequest):
    username = get_username(request.github_token)
    return delete_file(
        request.github_token,
        username,
        request.repo_name,
        request.path,
        request.commit_message
    )


@app.post("/github/delete-repo")
@require_permission("delete_repo")
def delete_repo_endpoint(request: DeleteRepoRequest):
    username = get_username(request.github_token)
    return delete_repo(
        request.github_token,
        username,
        request.repo_name
    )


@app.post("/github/rename-repo")
@require_permission("rename_repo")
def rename_repo_endpoint(request: RenameRepoRequest):
    username = get_username(request.github_token)
    return rename_repo(
        request.github_token,
        username,
        request.old_repo_name,
        request.new_repo_name
    )


@app.post("/github/rename-file")
@require_permission("rename_file")
def rename_file_endpoint(request: RenameFileRequest):
    username = get_username(request.github_token)
    return rename_file(
        request.github_token,
        username,
        request.repo_name,
        request.old_path,
        request.new_path,
        request.commit_message
    )


@app.post("/repo/edit-description")
def edit_description(data: EditDescriptionRequest):
    scopes = analyze_token_permissions(data.token)

    if not can_execute_action("edit_description", scopes):
        return {"error": "Insufficient token permissions"}

    return edit_repo_description(
        data.token,
        data.username,
        data.repo,
        data.description
    )


@app.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    # Client should delete token on success
    return {
        "message": "Logged out successfully. Please delete token on client side."
    }

# =========================================================
# ❤️ HEALTH CHECK
# =========================================================
@app.get("/")
def root():
    return {
        "status": "RUNNING",
        "message": "Super Assistant GitHub Automation is live 🚀"
    }
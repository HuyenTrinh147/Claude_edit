"""Google Drive: create a folder per project and upload the script / plan / renders.

Auth (pick one, set in .env):
* GOOGLE_OAUTH_CLIENT_FILE — OAuth "Desktop app" client JSON; first run opens a browser to log in,
  the token is cached at GOOGLE_TOKEN_FILE. Best for a personal Gmail account.
* GOOGLE_SERVICE_ACCOUNT_FILE — service account key. Service accounts have no storage quota of their
  own, so share a Shared Drive folder with the account and set GOOGLE_DRIVE_PARENT_ID to it.

Scope is drive.file: vedit only sees files and folders it created itself.
"""

from __future__ import annotations

from pathlib import Path

from .config import Settings

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
FOLDER_MIME = "application/vnd.google-apps.folder"
SUBFOLDERS = {"source": "01_Nguon", "script": "02_Kich_ban", "renders": "03_Video_xuat"}


class DriveError(RuntimeError):
    pass


def _service(settings: Settings):
    try:
        from google.oauth2 import service_account
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError as e:
        raise DriveError("Chưa cài thư viện Google: pip install 'vedit[gdrive]'") from e

    if settings.gdrive_service_account:
        creds = service_account.Credentials.from_service_account_file(
            str(settings.gdrive_service_account), scopes=SCOPES)
    elif settings.gdrive_oauth_client:
        token_path = settings.gdrive_token
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES) if token_path.exists() else None
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        if not creds or not creds.valid:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(str(settings.gdrive_oauth_client), SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text(creds.to_json(), encoding="utf-8")
    else:
        raise DriveError(
            "Chưa cấu hình Google Drive. Đặt GOOGLE_OAUTH_CLIENT_FILE (khuyên dùng) hoặc "
            "GOOGLE_SERVICE_ACCOUNT_FILE trong .env — xem README mục Google Drive.")
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _q(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def ensure_folder(service, name: str, parent_id: str | None) -> str:
    query = f"name = '{_q(name)}' and mimeType = '{FOLDER_MIME}' and trashed = false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    found = service.files().list(q=query, fields="files(id)", pageSize=1,
                                 supportsAllDrives=True, includeItemsFromAllDrives=True).execute().get("files", [])
    if found:
        return found[0]["id"]
    body = {"name": name, "mimeType": FOLDER_MIME, **({"parents": [parent_id]} if parent_id else {})}
    return service.files().create(body=body, fields="id", supportsAllDrives=True).execute()["id"]


def upload(service, path: Path, parent_id: str, as_google_doc: bool = False) -> dict:
    """Upload (or update in place, matched by name) a file. Returns {id, name, link}."""
    from googleapiclient.http import MediaFileUpload

    mime = {".md": "text/markdown", ".json": "application/json", ".mp4": "video/mp4",
            ".jpg": "image/jpeg", ".png": "image/png", ".txt": "text/plain"}.get(path.suffix.lower(),
                                                                                  "application/octet-stream")
    name = path.stem if as_google_doc else path.name
    media = MediaFileUpload(str(path), mimetype=mime, resumable=path.stat().st_size > 5 * 1024 * 1024)
    existing = service.files().list(
        q=f"name = '{_q(name)}' and '{parent_id}' in parents and trashed = false", fields="files(id)", pageSize=1,
        supportsAllDrives=True, includeItemsFromAllDrives=True).execute().get("files", [])
    fields = "id, name, webViewLink"
    if existing:
        meta = service.files().update(fileId=existing[0]["id"], media_body=media, fields=fields,
                                      supportsAllDrives=True).execute()
    else:
        body = {"name": name, "parents": [parent_id]}
        if as_google_doc:
            body["mimeType"] = "application/vnd.google-apps.document"
        meta = service.files().create(body=body, media_body=media, fields=fields, supportsAllDrives=True).execute()
    return {"id": meta["id"], "name": meta["name"], "link": meta.get("webViewLink")}


def setup_project_folders(settings: Settings, project) -> dict:
    """Create <root>/<project>/{01_Nguon, 02_Kich_ban, 03_Video_xuat}; store ids in project.json."""
    service = _service(settings)
    root = settings.gdrive_parent_id or ensure_folder(service, settings.gdrive_root_name, None)
    folder = ensure_folder(service, project.slug, root)
    info = {"folder_id": folder, "url": f"https://drive.google.com/drive/folders/{folder}",
            "subfolders": {key: ensure_folder(service, name, folder) for key, name in SUBFOLDERS.items()}}
    project.data["drive"] = info
    project.save()
    return info


def sync_project(settings: Settings, project, *, renders: bool = True, source: bool = False, log=print) -> dict:
    """Upload script files (script.md as a Google Doc), the edit plan and, optionally, renders / source video."""
    info = project.data.get("drive") or setup_project_folders(settings, project)
    service = _service(settings)
    sub = info["subfolders"]
    uploaded = []

    def put(path: Path, folder: str, as_doc: bool = False) -> None:
        if not path.exists():
            return
        try:
            uploaded.append(upload(service, path, sub[folder], as_google_doc=as_doc))
        except Exception as e:  # Markdown->Docs conversion can be refused; fall back to a plain file
            if not as_doc:
                raise
            log(f"    (không chuyển được {path.name} sang Google Docs: {e}; tải lên dạng file)")
            uploaded.append(upload(service, path, sub[folder]))
        log(f"    ↑ {path.name}")

    put(project.script_dir / "script.md", "script", as_doc=True)
    put(project.script_dir / "script.json", "script")
    put(project.plan_path, "script")
    if renders:
        for f in sorted(project.renders_dir.glob("*")):
            if f.suffix.lower() in (".mp4", ".mov", ".jpg") and not f.name.startswith("preview"):
                put(f, "renders")
    if source and project.input_path.exists():
        put(project.input_path, "source")
    return {"url": info["url"], "files": uploaded}

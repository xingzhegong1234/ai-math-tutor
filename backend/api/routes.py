"""FastAPI routes for the AI Math Tutor."""

import base64
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from ..config import UPLOAD_DIR
from ..models import database as db
from ..services.prompts import SYSTEM_PROMPT, SOLVE_PROMPT, CHECK_PROMPT, SIMILAR_PROMPT, CONCEPT_PROMPT
from .mimo import MiMoClient

router = APIRouter(prefix="/api", tags=["api"])

# Lazy-init client (avoids crash on import when API key is missing)
_mimo: MiMoClient | None = None


def get_mimo() -> MiMoClient:
    global _mimo
    if _mimo is None:
        _mimo = MiMoClient()
    return _mimo


# ─── Request/Response schemas ───────────────────────────────────────

class ChatRequest(BaseModel):
    conversation_id: int | None = None
    message: str
    mode: str = "solve"  # solve | check | similar | concept
    reasoning: bool = False


class ChatResponse(BaseModel):
    conversation_id: int
    reply: str


# ─── Routes ─────────────────────────────────────────────────────────

@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/conversations")
def list_conversations(bookmarked: bool = False):
    return db.get_conversations(bookmarked)


@router.get("/conversations/{conv_id}")
def get_conversation(conv_id: int):
    conv = db.get_conversation(conv_id)
    if not conv:
        raise HTTPException(404, "对话不存在")
    messages = db.get_messages(conv_id)
    return {"conversation": conv, "messages": messages}


@router.delete("/conversations/{conv_id}")
def delete_conversation(conv_id: int):
    conv = db.get_conversation(conv_id)
    if not conv:
        raise HTTPException(404, "对话不存在")
    db.delete_conversation(conv_id)
    return {"status": "deleted"}


@router.post("/conversations/{conv_id}/bookmark")
def bookmark_conversation(conv_id: int):
    conv = db.get_conversation(conv_id)
    if not conv:
        raise HTTPException(404, "对话不存在")
    bookmarked = db.toggle_bookmark(conv_id)
    return {"bookmarked": bookmarked}


def _get_prompt_for_mode(mode: str) -> str:
    prompts = {
        "solve": SOLVE_PROMPT,
        "check": CHECK_PROMPT,
        "similar": SIMILAR_PROMPT,
        "concept": CONCEPT_PROMPT,
    }
    return prompts.get(mode, SOLVE_PROMPT)


@router.post("/chat")
async def chat(
    conversation_id: int | None = Form(None),
    message: str = Form(...),
    mode: str = Form("solve"),
    reasoning: bool = Form(False),
    image: UploadFile | None = None,
):
    mimo = get_mimo()

    # Create or reuse conversation
    if conversation_id is None:
        # Auto-title: use first 20 chars of message
        title = message.strip()[:30] + ("…" if len(message) > 30 else "")
        conversation_id = db.create_conversation(title)
    else:
        conv = db.get_conversation(conversation_id)
        if not conv:
            raise HTTPException(404, "对话不存在")

    # Handle image upload
    image_b64 = None
    image_path = ""
    if image and image.filename:
        ext = image.filename.rsplit(".", 1)[-1] if "." in image.filename else "jpg"
        safe_name = f"{uuid.uuid4().hex}.{ext}"
        save_path = UPLOAD_DIR / safe_name
        image_path = safe_name
        content = await image.read()
        save_path.write_bytes(content)
        image_b64 = base64.b64encode(content).decode("utf-8")

    # Save user message
    db.add_message(conversation_id, "user", message, image_path)

    # Build the prompt
    mode_prompt = _get_prompt_for_mode(mode)
    full_message = f"{message}\n\n{mode_prompt}"

    # Call MiMo API
    try:
        response = mimo.chat(
            system_prompt=SYSTEM_PROMPT,
            user_message=full_message,
            image_url=image_b64,
            stream=False,
            reasoning=reasoning,
        )
        reply = response.choices[0].message.content or ""
    except Exception as e:
        raise HTTPException(502, f"MiMo API 调用失败: {str(e)}")

    # Save assistant reply
    db.add_message(conversation_id, "assistant", reply)

    return {"conversation_id": conversation_id, "reply": reply}


# ─── Alternative: JSON body version of chat (no file upload) ────────

@router.post("/chat/json")
def chat_json(req: ChatRequest):
    """Chat endpoint accepting JSON body (text-only, no image)."""
    mimo = get_mimo()

    if req.conversation_id is None:
        title = req.message.strip()[:30] + ("…" if len(req.message) > 30 else "")
        conversation_id = db.create_conversation(title)
    else:
        conversation_id = req.conversation_id
        conv = db.get_conversation(conversation_id)
        if not conv:
            raise HTTPException(404, "对话不存在")

    db.add_message(conversation_id, "user", req.message)

    mode_prompt = _get_prompt_for_mode(req.mode)
    full_message = f"{req.message}\n\n{mode_prompt}"

    try:
        response = mimo.chat(
            system_prompt=SYSTEM_PROMPT,
            user_message=full_message,
            stream=False,
            reasoning=req.reasoning,
        )
        reply = response.choices[0].message.content or ""
    except Exception as e:
        raise HTTPException(502, f"MiMo API 调用失败: {str(e)}")

    db.add_message(conversation_id, "assistant", reply)

    return {"conversation_id": conversation_id, "reply": reply}

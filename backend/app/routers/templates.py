"""API Router for reusable email templates."""

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.campaigns import EmailTemplate
from app.routers.emails import get_current_user_id

router = APIRouter(prefix="/api/v1/templates", tags=["Templates"])


class TemplateInput(BaseModel):
    title: str
    subject: str
    body_html: str
    body_text: str | None = None
    category: str | None = None
    is_favorite: bool = False


@router.get("")
async def list_templates(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Lists reusable email templates."""
    stmt = (
        select(EmailTemplate)
        .where(EmailTemplate.user_id == user_id)
        .order_by(desc(EmailTemplate.is_favorite), desc(EmailTemplate.updated_at))
    )
    result = await db.execute(stmt)
    templates = result.scalars().all()
    return templates


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_template(
    payload: TemplateInput,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Creates a new template."""
    template = EmailTemplate(
        user_id=user_id,
        title=payload.title,
        subject=payload.subject,
        body_html=payload.body_html,
        body_text=payload.body_text,
        category=payload.category,
        is_favorite=payload.is_favorite,
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Deletes a template."""
    template = (
        await db.execute(
            select(EmailTemplate).where(EmailTemplate.id == template_id, EmailTemplate.user_id == user_id)
        )
    ).scalars().first()
    if template:
        await db.delete(template)
        await db.commit()

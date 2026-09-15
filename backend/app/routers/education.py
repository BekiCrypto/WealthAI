from fastapi import APIRouter, HTTPException

from app.schemas.common import IndicatorEducation
from app.services.education.glossary import INDICATOR_GLOSSARY, get_education

router = APIRouter(prefix="/education", tags=["education"])


@router.get("", response_model=list[IndicatorEducation])
def list_indicator_briefings():
    """The full glossary of hand-written indicator briefings -- a standalone
    learning resource independent of any specific scheduled event.
    """
    return [briefing.__dict__ for briefing in INDICATOR_GLOSSARY.values()]


@router.get("/{name}", response_model=IndicatorEducation)
def indicator_briefing(name: str, category: str = "growth"):
    """A single indicator's briefing, by its exact calendar name. Falls back
    to a generic per-category briefing (via `category`) if there's no
    hand-written entry for this exact name yet.
    """
    if name not in INDICATOR_GLOSSARY and category not in (
        "inflation",
        "employment",
        "growth",
        "central_bank",
    ):
        raise HTTPException(status_code=404, detail=f"No briefing for '{name}' and unrecognized category '{category}'")
    return get_education(name, category).__dict__

from app.crud.draft_crud import draft_crud
from app.schemas.draft_schema import DraftCreate, DraftRead
from app.utils.pdf_extractor import extract_text_from_pdf
from app.utils.agent import summary_agent

async def draft_create(file, db, current_user):
    draft = extract_text_from_pdf(file.file)
    summary = await summary_agent.run("Execute Summary!")
    draft_in = DraftCreate(draft=draft, summary=summary.output)
    draft = await draft_crud.create(db, obj_in=draft_in, user_id=current_user.id)
    return draft

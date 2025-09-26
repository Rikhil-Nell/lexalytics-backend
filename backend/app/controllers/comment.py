from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import UploadFile, HTTPException
import csv
import io

from app.schemas.comment_schema import CommentCreate
from app.crud.comment_crud import comment_crud
from app.utils.agent import analysis_agent  # Your custom agent

async def add_comment_controller(
    draft_id: UUID,
    comment_in: CommentCreate,
    db: AsyncSession,
):
    # Use your analysis agent for sentiment
    sentiment = await analysis_agent.run(comment_in.comment)
    comment_in.sentiment_analysis = sentiment.output.sentiment_analysis
    comment_in.sentiment_score = sentiment.output.sentiment_score
    comment_in.sentiment_keywords = sentiment.output.sentiment_keywords
    comment = await comment_crud.create(db, obj_in=comment_in, draft_id=draft_id)
    return comment

async def add_comments_from_csv_controller(
    draft_id: UUID,
    file: UploadFile,
    db: AsyncSession,
):
    contents = await file.read()
    decoded = contents.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))
    comments: list[CommentCreate] = []
    for row in reader:
        comment_text = row.get("comment")
        if comment_text:
            sentiment = await analysis_agent.run(comment_text)
            comments.append(CommentCreate(
                comment=comment_text,
                sentiment_analysis=sentiment.output.sentiment_analysis,
                sentiment_score=sentiment.output.sentiment_score,
                sentiment_keywords=sentiment.output.sentiment_keywords
            ))
    if not comments:
        raise HTTPException(status_code=400, detail="No valid comments found in CSV")
    created = await comment_crud.create_many(db, objs_in=comments, draft_id=draft_id)
    return created

async def get_comments_by_draft_controller(
    draft_id: UUID,
    limit: int,
    db: AsyncSession,
):
    return await comment_crud.get_by_draft_id(db, draft_id, limit)
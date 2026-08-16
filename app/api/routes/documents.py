import uuid
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Response, UploadFile, status
from sqlalchemy import select

from app.api.dependencies import SessionDep, SettingsDep
from app.models import Document
from app.schemas import DocumentResponse
from app.services.documents import ingest_pdf
from app.services.pdf_parser import PDFValidationError

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: Annotated[UploadFile, File()],
    session: SessionDep,
    settings: SettingsDep,
) -> Document:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Only PDF files are supported")

    max_bytes = settings.max_upload_mb * 1024 * 1024
    data = await file.read(max_bytes + 1)
    await file.close()
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {settings.max_upload_mb} MB upload limit",
        )

    try:
        return await ingest_pdf(
            session,
            settings,
            filename=file.filename,
            content_type=file.content_type or "application/pdf",
            data=data,
        )
    except PDFValidationError as exc:
        await session.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        await session.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("", response_model=list[DocumentResponse])
async def list_documents(session: SessionDep) -> list[Document]:
    statement = select(Document).order_by(Document.created_at.desc())
    return list((await session.scalars(statement)).all())


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    session: SessionDep,
) -> Response:
    document = await session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    await session.delete(document)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

from typing import AsyncIterator

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.db import get_session
from app.models import Note, Notebook, NoteSchema


class CreateNote:
    def __init__(self, session: async_sessionmaker = Depends(get_session)) -> None:
        self.async_session = session

    async def execute(self, notebook_id: int, title: str, content: str) -> NoteSchema:
        async with self.async_session.begin() as session:
            notebook = await Notebook.read_by_id(session, notebook_id)
            if not notebook:
                raise HTTPException(status_code=404)
            note = await Note.create(session, notebook.id, title, content)
            return NoteSchema.from_orm(note)


class ReadAllNote:
    def __init__(self, session: async_sessionmaker = Depends(get_session)) -> None:
        self.async_session = session

    async def execute(self) -> AsyncIterator[NoteSchema]:
        async with self.async_session() as session:
            async for note in Note.read_all(session):
                yield NoteSchema.from_orm(note)


class ReadNote:
    def __init__(self, session: async_sessionmaker = Depends(get_session)) -> None:
        self.async_session = session

    async def execute(self, note_id: int) -> NoteSchema:
        async with self.async_session() as session:
            note = await Note.read_by_id(session, note_id)
            if not note:
                raise HTTPException(status_code=404)
            return NoteSchema.from_orm(note)


class UpdateNote:
    def __init__(self, session: async_sessionmaker = Depends(get_session)) -> None:
        self.async_session = session

    async def execute(self, note_id: int, notebook_id: int, title: str, content: str) -> NoteSchema:
        async with self.async_session.begin() as session:
            note = await Note.read_by_id(session, note_id)
            if not note:
                raise HTTPException(status_code=404)

            if note.notebook_id != notebook_id:
                notebook = await Notebook.read_by_id(session, notebook_id)
                if not notebook:
                    raise HTTPException(status_code=404)
                notebook_id_ = notebook.id
            else:
                notebook_id_ = note.notebook_id

            await note.update(session, notebook_id_, title, content)
            await session.refresh(note)
            return NoteSchema.from_orm(note)


class DeleteNote:
    def __init__(self, session: async_sessionmaker = Depends(get_session)) -> None:
        self.async_session = session

    async def execute(self, note_id: int) -> None:
        async with self.async_session.begin() as session:
            note = await Note.read_by_id(session, note_id)
            if not note:
                return
            await Note.delete(session, note)

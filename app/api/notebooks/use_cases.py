from typing import AsyncIterator

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.db import get_session
from app.models import Note, Notebook, NotebookSchema


class CreateNotebook:
    def __init__(self, session: async_sessionmaker = Depends(get_session)) -> None:
        self.async_session = session

    async def execute(self, title: str, notes: list[int]) -> NotebookSchema:
        async with self.async_session.begin() as session:
            exist_notes = [n async for n in Note.read_by_ids(session, note_ids=notes)]
            if len(exist_notes) != len(notes):
                raise HTTPException(status_code=404)
            notebook = await Notebook.create(session, title, exist_notes)
            return NotebookSchema.from_orm(notebook)


class ReadAllNotebook:
    def __init__(self, session: async_sessionmaker = Depends(get_session)) -> None:
        self.async_session = session

    async def execute(self) -> AsyncIterator[NotebookSchema]:
        async with self.async_session() as session:
            async for notebook in Notebook.read_all(session, include_notes=True):
                yield NotebookSchema.from_orm(notebook)


class ReadNotebook:
    def __init__(self, session: async_sessionmaker = Depends(get_session)) -> None:
        self.async_session = session

    async def execute(self, notebook_id: int) -> NotebookSchema:
        async with self.async_session() as session:
            notebook = await Notebook.read_by_id(session, notebook_id, include_notes=True)
            if not notebook:
                raise HTTPException(status_code=404)
            return NotebookSchema.from_orm(notebook)


class UpdateNotebook:
    def __init__(self, session: async_sessionmaker = Depends(get_session)) -> None:
        self.async_session = session

    async def execute(self, notebook_id: int, title: str, notes: list[int]) -> NotebookSchema:
        async with self.async_session.begin() as session:
            notebook = await Notebook.read_by_id(session, notebook_id, include_notes=True)
            if not notebook:
                raise HTTPException(status_code=404)

            exist_notes = [n async for n in Note.read_by_ids(session, note_ids=notes)]
            if len(exist_notes) != len(notes):
                raise HTTPException(status_code=404)
            await notebook.update(session, title, exist_notes)
            await session.refresh(notebook)
            return NotebookSchema.from_orm(notebook)


class DeleteNotebook:
    def __init__(self, session: async_sessionmaker = Depends(get_session)) -> None:
        self.async_session = session

    async def execute(self, notebook_id: int) -> None:
        async with self.async_session.begin() as session:
            notebook = await Notebook.read_by_id(session, notebook_id)
            if not notebook:
                return
            await Notebook.delete(session, notebook)

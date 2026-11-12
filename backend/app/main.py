"""FastAPI API for the cat archive, persisted in a local SQLite database."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="喵家档案 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)


class CatInput(BaseModel):
    name: Annotated[str, Field(max_length=40)]
    photo: str = ""
    breed: Annotated[str, Field(max_length=60)] = ""
    birthday: str = ""
    gender: str = ""
    personality: Annotated[str, Field(max_length=100)] = ""
    notes: Annotated[str, Field(max_length=1000)] = ""

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("猫咪名字不能为空")
        return value


class Cat(CatInput):
    id: str
    createdAt: str
    updatedAt: str


def database_path() -> Path:
    configured_path = os.environ.get("MIAOJIA_DB_PATH")
    if configured_path:
        return Path(configured_path)
    return Path(__file__).resolve().parents[1] / "data" / "cats.sqlite3"


def connect_db() -> sqlite3.Connection:
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS cats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            photo_data TEXT NOT NULL DEFAULT '',
            breed TEXT NOT NULL DEFAULT '',
            birthday TEXT NOT NULL DEFAULT '',
            gender TEXT NOT NULL DEFAULT '',
            personality TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT ''
        )
        """
    )
    columns = {row["name"] for row in connection.execute("PRAGMA table_info(cats)")}
    if "updated_at" not in columns:
        connection.execute("ALTER TABLE cats ADD COLUMN updated_at TEXT NOT NULL DEFAULT ''")
    connection.execute("UPDATE cats SET updated_at = created_at WHERE updated_at = ''")
    connection.commit()
    return connection


def row_to_cat(row: sqlite3.Row) -> Cat:
    return Cat(
        id=str(row["id"]),
        name=row["name"],
        photo=row["photo_data"],
        breed=row["breed"],
        birthday=row["birthday"],
        gender=row["gender"],
        personality=row["personality"],
        notes=row["notes"],
        createdAt=row["created_at"],
        updatedAt=row["updated_at"],
    )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/message")
def get_message() -> dict[str, str]:
    return {"message": "喵家档案后端连接成功"}


@app.get("/api/cats", response_model=list[Cat])
def list_cats() -> list[Cat]:
    with connect_db() as connection:
        rows = connection.execute(
            "SELECT * FROM cats ORDER BY updated_at DESC, created_at DESC"
        ).fetchall()
    return [row_to_cat(row) for row in rows]


@app.post("/api/cats", response_model=Cat, status_code=201)
def create_cat(cat: CatInput) -> Cat:
    timestamp = now_iso()
    values = cat.model_dump()
    with connect_db() as connection:
        cursor = connection.execute(
            """INSERT INTO cats
               (name, photo_data, breed, birthday, gender, personality, notes, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                values["name"],
                values["photo"],
                values["breed"],
                values["birthday"],
                values["gender"],
                values["personality"],
                values["notes"],
                timestamp,
                timestamp,
            ),
        )
        cat_id = str(cursor.lastrowid)
    return Cat(id=cat_id, **values, createdAt=timestamp, updatedAt=timestamp)


@app.get("/api/cats/{cat_id}", response_model=Cat)
def get_cat(cat_id: str) -> Cat:
    with connect_db() as connection:
        row = connection.execute("SELECT * FROM cats WHERE id = ?", (cat_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="找不到这份猫咪档案")
    return row_to_cat(row)


@app.put("/api/cats/{cat_id}", response_model=Cat)
def update_cat(cat_id: str, cat: CatInput) -> Cat:
    with connect_db() as connection:
        existing = connection.execute(
            "SELECT created_at FROM cats WHERE id = ?", (cat_id,)
        ).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="找不到这份猫咪档案")

        values = cat.model_dump()
        timestamp = now_iso()
        connection.execute(
            """UPDATE cats SET
               name = ?, photo_data = ?, breed = ?, birthday = ?, gender = ?,
               personality = ?, notes = ?, updated_at = ?
               WHERE id = ?""",
            (
                values["name"],
                values["photo"],
                values["breed"],
                values["birthday"],
                values["gender"],
                values["personality"],
                values["notes"],
                timestamp,
                cat_id,
            ),
        )
        created_at = existing["created_at"]
    return Cat(
        id=cat_id,
        **values,
        createdAt=created_at,
        updatedAt=timestamp,
    )


@app.delete("/api/cats/{cat_id}", status_code=204)
def delete_cat(cat_id: str) -> Response:
    with connect_db() as connection:
        result = connection.execute("DELETE FROM cats WHERE id = ?", (cat_id,))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="找不到这份猫咪档案")
    return Response(status_code=204)

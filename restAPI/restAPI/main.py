from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from collections import Counter
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db, BookDB
from auth import verify_api_key

# Создание экземпляра приложения FastAPI
app = FastAPI(
title="Books API",
description="REST API для управления библиотекой книг",
version="1.0.0"
)

# Модель данных для книги (Pydantic схема)
class Book(BaseModel):
    id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=200, description="Название книги")
    author: str = Field(..., min_length=1, max_length=100, description="Автор книги")
    year: int = Field(..., ge=1000, le=datetime.now().year, description="Год издания")
    isbn: Optional[str] = Field(None, min_length=10, max_length=13, description="ISBN книги")

    class Config:
        json_schema_extra = {
        "example": {
        "title": "Мастер и Маргарита",
        "author": "Михаил Булгаков",
        "year": 1967,
        "isbn": "9785170123456"
        }
    }


# Модель для обновления книги (все поля опциональны)
class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=1000, le=datetime.now().year)
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)

# Временное хранилище данных (в реальном приложении используется база данных)
books_db: List[Book] = [
    Book(id=1, title="Война и мир", author="Лев Толстой", year=1869, isbn="9785170987654"),
    Book(id=2, title="Преступление и наказание", author="Федор Достоевский", year=1866, isbn="9785170876543"),
    Book(id=3, title="Евгений Онегин", author="Александр Пушкин", year=1833, isbn="9785170765432")
]

# Счетчик для генерации ID
next_id = 4


# Корневой эндпоинт
@app.get("/", tags=["Root"])
async def root():
    """
    Корневой эндпоинт API.
    Возвращает приветственное сообщение и ссылки на документацию.
    """
    return {
        "message": "Добро пожаловать в Books API!",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# GET /api/books - Получение списка всех книг
@app.get("/api/books", response_model=List[Book], tags=["Books"])
async def get_books(db: Session = Depends(get_db)):
    """Получить список всех книг из базы данных."""

    books = db.query(BookDB).all()

    return books


# GET /api/books/{book_id} - Получение книги по ID
@app.get("/api/books/{book_id}", response_model=Book, tags=["Books"])
async def get_book(book_id: int):
    """
    Получить книгу по ID.
    - **book_id**: ID книги (целое число)
    Возвращает информацию о книге с указанным ID.
    Если книга не найдена, возвращается ошибка 404.
    """
    for book in books_db:
        if book.id == book_id:
            return book
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Книга с ID {book_id} не найдена"
    )


# POST /api/books - Создание новой книги
@app.post("/api/books", response_model=Book, status_code=status.HTTP_201_CREATED, tags=["Books"])
async def create_book(book: Book, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    """Создать новую книгу в базе данных."""
    db_book = BookDB(**book.model_dump(exclude={"id"}))
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


# PUT /api/books/{book_id} - Полное обновление книги
@app.put("/api/books/{book_id}", response_model=Book, tags=["Books"])
async def update_book(book_id: int, updated_book: Book):
    """
    Полностью обновить информацию о книге.
    - **book_id**: ID книги для обновления
    - **updated_book**: Новые данные книги (все поля обязательны)
    Заменяет все данные книги новыми значениями.
    Если книга не найдена, возвращается ошибка 404.
    """
    for index, book in enumerate(books_db):
        if book.id == book_id:
            # Сохраняем ID
            updated_book.id = book_id
            books_db[index] = updated_book
            return updated_book
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Книга с ID {book_id} не найдена"
    )


# PATCH /api/books/{book_id} - Частичное обновление книги
@app.patch("/api/books/{book_id}", response_model=Book, tags=["Books"])
async def partial_update_book(book_id: int, book_update: BookUpdate):
    """
    Частично обновить информацию о книге.
    - **book_id**: ID книги для обновления
    - **book_update**: Данные для обновления (только указанные поля будут изменены)
    Обновляет только те поля, которые были переданы в запросе.
    Если книга не найдена, возвращается ошибка 404.
    """
    for book in books_db:
        if book.id == book_id:
            # Обновляем только переданные поля
            update_data = book_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(book, field, value)
            return book
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Книга с ID {book_id} не найдена"
    )


# DELETE /api/books/{book_id} - Удаление книги
@app.delete("/api/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Books"])
async def delete_book(book_id: int):
    """
    Удалить книгу по ID.
    - **book_id**: ID книги для удаления
    Удаляет книгу из системы.
    Если книга не найдена, возвращается ошибка 404.
    """
    for index, book in enumerate(books_db):
        if book.id == book_id:
            books_db.pop(index)
            return
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Книга с ID {book_id} не найдена"
    )


@app.get("/api/book/stats", tags=["Statistics"])
async def get_statistics():
    """
    Получить статистику по книгам.
    Возвращает общее количество книг, распределение по авторам и векам.
    """
    total_books = len(books_db)
    authors = Counter(book.author for book in books_db)
    centuries = Counter(book.year // 100 + 1 for book in books_db)
    return {
        "total_books": total_books,
        "books_by_author": dict(authors),
        "books_by_century": {f"{century} век": count for century, count in centuries.items()}
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)




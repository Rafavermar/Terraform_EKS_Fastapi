from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, TypeAdapter
from typing import List, Optional
import csv
import os
import logging

data_file = os.environ.get("DATA_FILE", default='../data/books.csv')

app = FastAPI(title="Books API", version="1.0.0")


##MODEL
class Book(BaseModel):
    id: int
    title: str
    author: str
    basic_discount: Optional[float] = None
    premium_discount: Optional[float] = None


@app.get("/books", response_model=list[Book], tags=["books"])
async def books() -> List[Book]:
    """Get list of books."""
    books = get_books_data(data_file)
    return books


@app.get("/book/{book_id}", response_model=Book, tags=["books"])
async def books(book_id: int) -> Book:
    """Get book by id."""
    book: Book = find_book(book_id, data_file)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


## Read File and return list of books
def get_books_data(file_path: str) -> List[Book]:
    data = []
    try:
        with open(file_path) as file:
            for row in csv.DictReader(file, delimiter=",", quoting=csv.QUOTE_NONNUMERIC):
                row["id"] = int(row["id"])
                data.append(dict(row))
    except Exception as e:
        logging.error(e)

    BookList = TypeAdapter(List[Book])
    books = BookList.validate_python(data)
    return books


## Get all book and find one by ID
def find_book(book_id: int, file_path: str) -> Optional[Book]:
    books = get_books_data(file_path)
    for b in books:
        if b.id == book_id:
            return b
    return None

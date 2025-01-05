from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import json
import httpx

app = FastAPI()

BOOKS_FILE = "books.json"

class Book(BaseModel):
    title: str
    author: str
    isbn: str
    description: Optional[str] = None
    is_read: Optional[bool] = False

def load_books():
    try:
        with open(BOOKS_FILE, "r") as file:
            return json.load(file)  
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_books(books):
    with open(BOOKS_FILE, "w") as file:
        json.dump(books, file, indent=4)  

def fetch_google_book(isbn: str):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = httpx.get(url)  
    if response.status_code == 200:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:  
            item = data["items"][0]
            volume_info = item["volumeInfo"]
            return {
                "title": volume_info.get("title", "Unknown"),
                "author": ", ".join(volume_info.get("authors", ["Unknown"])),
                "isbn": isbn,
                "description": volume_info.get("description", "No description available"),
                "is_read": False,
            }
        else:
            
            raise HTTPException(status_code=404, detail="Book not found in external API")
    else:
        
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch book details")

@app.get("/books/search")
def search_book(isbn: str = Query(...)):
    return fetch_google_book(isbn)  

@app.post("/books/search")
def search_and_add_book(isbn: str = Query(...)):
    book = fetch_google_book(isbn)  
    books = load_books()
    if any(b["isbn"] == isbn for b in books):
        raise HTTPException(status_code=400, detail="Book with this ISBN already exists")    
    books.append(book)
    save_books(books)
    return book


@app.get("/books", response_model=List[Book])
def get_books():
    return load_books()  

@app.get("/books/author/{author}", response_model=List[Book])
def get_books_by_author(author: str):
    books = load_books()
    result = [book for book in books if author.lower() in book["author"].lower()]
    if result:
        return result
    raise HTTPException(status_code=404, detail="No books found for the given author")


@app.get("/books/title/{title}", response_model=List[Book])
def get_books_by_title(title: str):
    books = load_books()
    result = [book for book in books if title.lower() in book["title"].lower()]
    if result:
        return result
    raise HTTPException(status_code=404, detail="No books found for the given title")


@app.get("/books/{isbn}", response_model=Book)
def get_book(isbn: str):
    books = load_books()
    for book in books:
        if book["isbn"] == isbn:
            return book  
    raise HTTPException(status_code=404, detail="Book not found")


@app.post("/books", response_model=Book)
def add_book(book: Book):
    books = load_books()
    if any(b["isbn"] == book.isbn for b in books):
        raise HTTPException(status_code=400, detail="Book with this ISBN already exists")
    books.append(book.model_dump())  
    save_books(books)
    return book


@app.put("/books/{isbn}", response_model=Book)
def update_book(isbn: str, updated_book: Book):
    books = load_books()
    for index, book in enumerate(books):
        if book["isbn"] == isbn:
            books[index] = updated_book.model_dump()  
            save_books(books)
            return updated_book
    raise HTTPException(status_code=404, detail="Book not found")


@app.delete("/books/{isbn}")
def delete_book(isbn: str):
    books = load_books()
    for book in books:
        if book["isbn"] == isbn:
            books.remove(book)  
            save_books(books)
            return {"message": "Book deleted successfully"}
    raise HTTPException(status_code=404, detail="Book not found")


@app.patch("/books/{isbn}/toggle-read", response_model=Book)
def toggle_read_status(isbn: str):
    books = load_books()
    for book in books:
        if book["isbn"] == isbn:
            book["is_read"] = not book["is_read"]  
            save_books(books)
            return book
    raise HTTPException(status_code=404, detail="Book not found")

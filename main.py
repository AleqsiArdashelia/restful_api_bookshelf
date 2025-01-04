from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import json
import httpx

app = FastAPI()

# Path to the JSON file used for storing book data locally
BOOKS_FILE = "books.json"

# Data model for a book, with title, author, ISBN, an optional description, and a read status
class Book(BaseModel):
    title: str
    author: str
    isbn: str
    description: Optional[str] = None
    is_read: Optional[bool] = False

# Function to load books from the JSON file
def load_books():
    try:
        with open(BOOKS_FILE, "r") as file:
            return json.load(file)  # Load and return book data as a list of dictionaries
    except (FileNotFoundError, json.JSONDecodeError):
        # Return an empty list if the file does not exist or contains invalid JSON
        return []

# Function to save books to the JSON file
def save_books(books):
    with open(BOOKS_FILE, "w") as file:
        json.dump(books, file, indent=4)  # Save book data with readable formatting

# Function to fetch book details from the Google Books API using an ISBN
def fetch_google_book(isbn: str):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = httpx.get(url)  # Make a GET request to the API
    if response.status_code == 200:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:  # Check if any book data is returned
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
            # Raise an error if the book is not found in the external API
            raise HTTPException(status_code=404, detail="Book not found in external API")
    else:
        # Raise an error if the API request fails
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch book details")

# Endpoint to search for book details using an ISBN
@app.get("/books/search")
def search_book(isbn: str = Query(...)):
    return fetch_google_book(isbn)  # Fetch and return book details from the API

# Endpoint to search for a book and add it to local storage
@app.post("/books/search")
def search_and_add_book(isbn: str = Query(...)):
    book = fetch_google_book(isbn)  # Fetch book details from the API

    # Load existing books and check for duplicates
    books = load_books()
    if any(b["isbn"] == isbn for b in books):
        raise HTTPException(status_code=400, detail="Book with this ISBN already exists")

    # Add the new book to local storage
    books.append(book)
    save_books(books)
    return book

# Endpoint to retrieve all stored books
@app.get("/books", response_model=List[Book])
def get_books():
    return load_books()  # Return all books from local storage

# Endpoint to retrieve a specific book by its ISBN
@app.get("/books/{isbn}", response_model=Book)
def get_book(isbn: str):
    books = load_books()
    for book in books:
        if book["isbn"] == isbn:
            return book  # Return the book if found
    raise HTTPException(status_code=404, detail="Book not found")

# Endpoint to retrieve books by author
@app.get("/books/author/{author}", response_model=List[Book])
def get_books_by_author(author: str):
    books = load_books()
    result = [book for book in books if author.lower() in book["author"].lower()]
    if result:
        return result
    raise HTTPException(status_code=404, detail="No books found for the given author")

# Endpoint to retrieve books by title
@app.get("/books/title/{title}", response_model=List[Book])
def get_books_by_title(title: str):
    books = load_books()
    result = [book for book in books if title.lower() in book["title"].lower()]
    if result:
        return result
    raise HTTPException(status_code=404, detail="No books found for the given title")

# Endpoint to add a new book to local storage
@app.post("/books", response_model=Book)
def add_book(book: Book):
    books = load_books()
    if any(b["isbn"] == book.isbn for b in books):
        raise HTTPException(status_code=400, detail="Book with this ISBN already exists")
    books.append(book.model_dump())  # Add the book to the list
    save_books(books)
    return book

# Endpoint to update the details of an existing book by ISBN
@app.put("/books/{isbn}", response_model=Book)
def update_book(isbn: str, updated_book: Book):
    books = load_books()
    for index, book in enumerate(books):
        if book["isbn"] == isbn:
            books[index] = updated_book.model_dump()  # Update the book details
            save_books(books)
            return updated_book
    raise HTTPException(status_code=404, detail="Book not found")

# Endpoint to delete a book from local storage by ISBN
@app.delete("/books/{isbn}")
def delete_book(isbn: str):
    books = load_books()
    for book in books:
        if book["isbn"] == isbn:
            books.remove(book)  # Remove the book from the list
            save_books(books)
            return {"message": "Book deleted successfully"}
    raise HTTPException(status_code=404, detail="Book not found")

# Endpoint to toggle the read status of a book
@app.patch("/books/{isbn}/toggle-read", response_model=Book)
def toggle_read_status(isbn: str):
    books = load_books()
    for book in books:
        if book["isbn"] == isbn:
            book["is_read"] = not book["is_read"]  # Flip the read status
            save_books(books)
            return book
    raise HTTPException(status_code=404, detail="Book not found")

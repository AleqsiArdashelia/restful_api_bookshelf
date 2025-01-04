# Bookshelf API

## Overview
The Bookshelf API is a FastAPI-based application for managing a personal collection of books. It enables users to search, store, and manage books using local storage and integrates with the Google Books API for fetching book details by ISBN.

---

## Features

- **Book Management**:
  - Add new books to local storage.
  - Retrieve all stored books or filter them by title, author, or ISBN.
  - Update book details or delete books.
  - Toggle the read status of books.

- **Integration with Google Books API**:
  - Fetch detailed information about books by ISBN and store them locally.

- **Local Storage**:
  - Persistent storage of books using a JSON file.

---

## File Structure

```
bookshelf_api/
├── main.py            # Main application file
├── books.json         # JSON file for local book storage
├── requirements.txt   # Dependencies required for the project
└── readme.md          # Project documentation
```

---

## Setup Instructions

### Prerequisites
1. Python 3.7+
2. FastAPI
3. Pydantic
4. HTTPx
5. Uvicorn (for running the server)

### Installation

1. Clone the repository:
    ```bash
    git clone <repository_url>
    cd bookshelf_api
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate    # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. (Optional) Create an empty `books.json` file for local storage:
    ```bash
    touch books.json
    ```
    - Ensure the file contains an empty array (`[]`) to avoid errors.

5. Run the application:
    ```bash
    uvicorn main:app --reload
    ```

---

## API Endpoints

### Base URL: `/`

### Resources

#### **`GET /books`**
- Retrieves all stored books.
- **Response**:
  ```json
  [
    {
      "title": "Book Title",
      "author": "Author Name",
      "isbn": "1234567890",
      "description": "Book description",
      "is_read": false
    }
  ]
  ```

#### **`POST /books`**
- Adds a new book to local storage.
- **Request Body**:
  ```json
  {
    "title": "Book Title",
    "author": "Author Name",
    "isbn": "1234567890",
    "description": "Optional description",
    "is_read": false
  }
  ```

#### **`GET /books/{isbn}`**
- Retrieves details of a specific book by ISBN.

#### **`PUT /books/{isbn}`**
- Updates an existing book's details by ISBN.
- **Request Body**:
  ```json
  {
    "title": "Updated Title",
    "author": "Updated Author",
    "isbn": "1234567890",
    "description": "Updated description",
    "is_read": true
  }
  ```

#### **`DELETE /books/{isbn}`**
- Deletes a book by ISBN.
- **Response**:
  ```json
  {
    "message": "Book deleted successfully"
  }
  ```

#### **`PATCH /books/{isbn}/toggle-read`**
- Toggles the read status of a book by ISBN.

#### **`GET /books/search`**
- Fetches book details from the Google Books API using an ISBN.
- **Query Parameter**: `isbn` (required).

#### **`POST /books/search`**
- Searches for a book by ISBN using the Google Books API and adds it to local storage if it doesn’t already exist.

#### **`GET /books/title/{title}`**
- Retrieves books matching a specific title.

#### **`GET /books/author/{author}`**
- Retrieves books by a specific author.

---

## Testing

You can test the API using:
- [FastAPI Interactive Docs](http://127.0.0.1:8000/docs)
- cURL commands
- [Postman](https://www.postman.com/)


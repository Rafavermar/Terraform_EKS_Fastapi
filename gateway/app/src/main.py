from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,TypeAdapter
from typing import List, Optional
import requests
import yaml
import os
from time import sleep

sleep(20)
main_config_path= os.environ.get("CONFIG_PATH", default='../conf.d/main.yml')

with open(main_config_path, 'r') as file:
    config = yaml.safe_load(file)

app = FastAPI(title="Gateway API", version="1.0.1")


## BEGIN MODEL
class Book(BaseModel):
    id: int 
    title: str 
    author: str
    basic_discount: Optional[float] = None
    premium_discount: Optional[float] = None

class Client(BaseModel):
    id: int 
    name: str 
    type: str

class outMsg(BaseModel):
    message: str
    book: Optional[Book] = None

## END MODEL

@app.get("/clients", response_model=list[Client], tags=["Clients"])
async def clients()->List[Client]:
    """Get list of clients."""
    books = get_clients_data()
    return books


@app.get("/books", response_model=list[Book], tags=["Books"])
async def books()->List[Book]:
    """Get list of books."""
    books= get_books_data()
    return books


@app.get("/book/{book_id}", response_model=outMsg, tags=["Personalized"])
async def book_with_personalized_msg(book_id:int, client_id:int | None = None )->outMsg:
    """Get book by id and personalized message for client."""
    msg= book_for_client(book_id, client_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Book not found")
    return msg


## Get list of books calling book API.
def get_books_data()->List[Book]:
    endpoint = f'{config["url"]["books"]}/books'
    resp = requests.get(endpoint)
    if resp.status_code == 200:
        data = resp.json()
    else: 
        data = []
    BookList= TypeAdapter(List[Book])
    books = BookList.validate_python(data)
    return books

## Get list of clients calling clients API.
def get_clients_data()->List[Client]:
    endpoint = f'{config["url"]["clients"]}/clients'
    resp = requests.get(endpoint)
    if resp.status_code == 200:
        data = resp.json()
    else: 
        data = []
    ClientList= TypeAdapter(List[Client])
    clients = ClientList.validate_python(data)
    return clients

## Get personalized message for client and book.
def get_msg(book:Book, client:Client) -> str: 
    if not client: 
        msg="Become client to get fantastic discounts!."
        if book.basic_discount > 0:
            msg+=f' You could have had a {book.basic_discount:.0%} discount just being client.'
    else: 
        msg=f'{client.name} thanks for keep buying with us'
        if book.basic_discount > 0 and client.type == "Basic":
            msg+=f' For this book you get {book.basic_discount:.0%} discount, just for being client.'
        elif book.premium_discount > 0 and client.type == "Premium":
            msg+=f' For this book you get  {book.premium_discount:.0%} discount, just for being premium client.'
    return msg

## Get Book and personalized message for client.
def book_for_client(book_id:int, client_id:int=None)->Optional[outMsg]:
    book_endpoint=f'{config["url"]["books"]}/book/{book_id}'
    book_resp = requests.get(book_endpoint)
    if book_resp.status_code != 200:
        return None
    Book_ta= TypeAdapter(Book)
    book = Book_ta.validate_python(book_resp.json())
    print(book)
    if (client_id):
        client_endpoint=f'{config["url"]["clients"]}/client/{client_id}'
        client_resp = requests.get(client_endpoint)
        if client_resp.status_code != 200:
            client=None
        else:
            Client_ta= TypeAdapter(Client)
            client = Client_ta.validate_python(client_resp.json())
    else:
        client = None
    msg:outMsg ={"book": book, "message": get_msg(book, client)}
    return msg





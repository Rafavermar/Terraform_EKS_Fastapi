from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, TypeAdapter
from typing import List, Optional
import csv
import os
import logging

data_file = os.environ.get("DATA_FILE", default='../data/clients.csv')

app = FastAPI(title="Clients API", version="1.0.0")


## MODEL
class Client(BaseModel):
    id: int
    name: str
    type: str


@app.get("/clients", response_model=list[Client], tags=["Clients"])
async def clients() -> List[Client]:
    """Get list of clients."""
    clients = get_clients_data(data_file)
    return clients


@app.get("/client/{client_id}", response_model=Client, tags=["Clients"])
async def get_client(client_id: int) -> Client:
    """Get client by id."""
    client: Client = find_client(client_id, data_file)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


## Read File and return list of clients
def get_clients_data(file_path: str) -> List[Client]:
    data = []
    try:
        with open(file_path) as file:
            for row in csv.DictReader(file, delimiter=",", quoting=csv.QUOTE_NONNUMERIC, dialect="excel"):
                row["id"] = int(row["id"])
                data.append(dict(row))
    except Exception as e:
        logging.error(e)

    ClientList = TypeAdapter(List[Client])
    clients = ClientList.validate_python(data)
    return clients


## Get all clients and find one by ID
def find_client(client_id: int, file_path: str) -> Optional[Client]:
    clients = get_clients_data(file_path)
    for c in clients:
        if c.id == client_id:
            return c
    return None

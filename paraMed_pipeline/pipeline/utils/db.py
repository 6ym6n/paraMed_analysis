"""
Database helper functions.

This module provides a unified way to obtain MongoDB clients, databases
and collections.  All database configuration is read from environment
variables with sensible defaults, so you can override the connection
URI or database name without modifying code.  To change the defaults,
create a `.env` file in your project and set `MONGO_URI` or
`MONGO_DB_NAME` accordingly.
"""

import os
from typing import Optional
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()


def get_client(uri: Optional[str] = None) -> MongoClient:
    """Return a MongoDB client.

    Parameters
    ----------
    uri : str, optional
        MongoDB connection URI.  If not provided, reads from the
        `MONGO_URI` environment variable or defaults to
        `mongodb://localhost:27017`.

    Returns
    -------
    MongoClient
        A connected MongoDB client instance.
    """
    mongo_uri = uri or os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(mongo_uri)
    return client


def get_db(db_name: Optional[str] = None, *, client: Optional[MongoClient] = None):
    """Return the default database handle.

    Parameters
    ----------
    db_name : str, optional
        Name of the database to return.  Defaults to the
        `MONGO_DB_NAME` environment variable or `paraMedProducts`.
    client : MongoClient, optional
        Reuse an existing client instead of creating a new one.

    Returns
    -------
    Database
        A PyMongo database object.
    """
    if client is None:
        client = get_client()
    name = db_name or os.getenv("MONGO_DB_NAME", "ParaMedAnalysis")
    return client[name]


def get_collection(collection_name: str, *, db_name: Optional[str] = None, client: Optional[MongoClient] = None):
    """Return a collection handle.

    Parameters
    ----------
    collection_name : str
        Name of the collection to access.
    db_name : str, optional
        Name of the database.  If omitted, uses the default from
        `get_db`.
    client : MongoClient, optional
        Existing Mongo client.

    Returns
    -------
    Collection
        A PyMongo collection object.
    """
    db = get_db(db_name=db_name, client=client)
    return db[collection_name]


__all__ = [
    "get_client",
    "get_db",
    "get_collection",
]
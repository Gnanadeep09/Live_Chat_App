# Real-Time Asynchronous Chat Gateway

A high-performance, multi-room chat backend built with Python, FastAPI WebSockets, and SQLAlchemy 2.0. This architecture uses a persistent, bi-directional communication layer to route live messages while utilizing a non-blocking database pipeline for permanent chat storage.

## Core Technical Features
* FastAPI WebSockets: Implements stateful connection routing using a centralized management class to manage multi-room concurrent communication.
* Asynchronous Pipeline: Uses aiosqlite and SQLAlchemy AsyncSession to prevent database operations from blocking the main event loop.
* Modern ORM Architecture: Utilizes SQLAlchemy 2.0 strict static type-mapping for structural database configurations.
* Data Validation: Enforces strict data integrity at the API layer using Pydantic v2 schemas to validate incoming payloads and filter outgoing responses.

## System Architecture
1. Handshake: The client establishes a continuous connection string via ws:// (local) or wss:// (production).
2. Session Allocation: The server isolates the socket stream by mapping individual room identifiers.
3. Broadcast & Log: Incoming payloads are parsed, asynchronously written to the database, and concurrently broadcast to all active listeners in the channel.

## Local Setup Instructions
1. Install Dependencies:
pip install fastapi uvicorn sqlalchemy aiosqlite pydantic

2. Run the Application Server:
uvicorn main:app --reload

3. Access Interactive API Documentation:
# PLY Navigator Backend

FastAPI + SQLite backend for the PLY indoor navigation project.

This directory can be separated and deployed as an independent backend project.
The frontend is expected to call the API endpoints listed below.

## Files

```text
backend/
  main.py             # FastAPI app, SQLite storage, A* path API
  requirements.txt    # Python dependencies
  .env.example        # Example runtime configuration
  .gitignore          # Backend-only ignore rules
  README.md           # Backend setup and deployment notes
```

Runtime-generated files such as `graph.db` and `__pycache__/` are not required
in source control.

## Requirements

- Python 3.10+
- SQLite, included with Python

Python packages:

```text
fastapi==0.115.12
uvicorn[standard]==0.34.0
pydantic>=2.0
```

## Environment Variables

| Name | Default | Description |
| --- | --- | --- |
| `DB_PATH` | `./graph.db` beside `main.py` | SQLite database file path |
| `CORS_ORIGINS` | `*` | Comma-separated allowed frontend origins |

Examples:

```powershell
$env:DB_PATH="C:\data\ply-navigator\graph.db"
$env:CORS_ORIGINS="http://localhost:5173,https://example.com"
```

For local development, copying `.env.example` to `.env` is useful as
documentation, but `main.py` does not require a dotenv package. Set environment
variables in your shell, hosting platform, or process manager.

## Install

Windows PowerShell:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

## Run

Development:

```powershell
cd backend
py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Production-style local run:

```powershell
cd backend
py -m uvicorn main:app --host 0.0.0.0 --port 8000
```

The frontend currently expects the backend at:

```text
http://localhost:8000
```

API docs:

```text
http://localhost:8000/docs
```

## API

### `GET /`

Health check.

Response:

```json
{ "status": "ok" }
```

### `POST /graph`

Stores the full navigation graph. Existing graph data is replaced.

Request body:

```json
{
  "nodes": [
    { "id": "room-1", "name": "Room 1", "type": "room", "x": 0, "y": 0, "z": 0 },
    { "id": "wp-1", "name": "Waypoint", "type": "waypoint", "x": 1, "y": 0, "z": 0 },
    { "id": "start-1", "name": "Start", "type": "start", "x": 0, "y": 1, "z": 0 }
  ],
  "edges": [
    { "id": "edge-1", "from": "room-1", "to": "wp-1" }
  ]
}
```

Response:

```json
{ "saved": true, "node_count": 3, "edge_count": 1 }
```

### `GET /graph`

Returns the latest stored graph.

If there is no saved graph:

```json
{ "nodes": [], "edges": [] }
```

### `GET /path?from=<id>&to=<id>`

Returns an A* path between two node IDs.

Response:

```json
{
  "path": [
    { "id": "room-1", "name": "Room 1", "type": "room", "x": 0, "y": 0, "z": 0 },
    { "id": "wp-1", "name": "Waypoint", "type": "waypoint", "x": 1, "y": 0, "z": 0 }
  ]
}
```

## Data Notes

- Node schema: `{ id, name, type, x, y, z }`
- Allowed node types: `room`, `waypoint`, `start`
- Edge schema: `{ id, from, to }`
- SQLite table: `graph(id, data, updated_at)`
- The graph is stored as one JSON document and the latest row is used.
- `graph.db` is runtime data. Do not commit it unless you intentionally want to
  ship a preloaded graph.

## Separation Plan

To split this backend into a separate repository:

1. Copy only the `backend/` directory contents into the new repository root.
2. Keep `main.py`, `requirements.txt`, `.env.example`, `.gitignore`, and
   `README.md`.
3. Exclude `graph.db`, `__pycache__/`, `.venv/`, and local `.env` files.
4. Deploy with `py -m uvicorn main:app --host 0.0.0.0 --port 8000` or the
   equivalent command for the target hosting platform.
5. Configure the frontend API base URL to point to the deployed backend.

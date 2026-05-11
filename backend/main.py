from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal
import sqlite3, json, os, math, heapq


BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "graph.db"))
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS graph (
                id INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


init_db()


# ── 스키마 ─────────────────────────────────────────────────────────────────────

class Node(BaseModel):
    id: str
    name: str
    type: Literal["room", "waypoint", "start"]
    x: float
    y: float
    z: float


class Edge(BaseModel):
    id: str
    from_: str = None
    to: str = None

    class Config:
        populate_by_name = True

    def __init__(self, **data):
        # JSON 키 "from" 은 Python 예약어라 별칭 처리
        if "from" in data:
            data["from_"] = data.pop("from")
        super().__init__(**data)


class GraphPayload(BaseModel):
    nodes: list[Node]
    edges: list[dict]  # from/to 그대로 받기 위해 dict 사용


# ── 엔드포인트 ────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/graph")
def save_graph(payload: GraphPayload):
    data = {
        "nodes": [n.model_dump() for n in payload.nodes],
        "edges": payload.edges,
    }
    with get_db() as conn:
        conn.execute("DELETE FROM graph")
        conn.execute("INSERT INTO graph (data) VALUES (?)", (json.dumps(data),))
        conn.commit()
    return {"saved": True, "node_count": len(payload.nodes), "edge_count": len(payload.edges)}


@app.get("/graph")
def load_graph():
    with get_db() as conn:
        row = conn.execute("SELECT data FROM graph ORDER BY id DESC LIMIT 1").fetchone()
    if row is None:
        return {"nodes": [], "edges": []}
    return json.loads(row["data"])


@app.get("/path")
def get_path(
    from_id: str = Query(..., alias="from"),
    to_id: str = Query(..., alias="to"),
):
    with get_db() as conn:
        row = conn.execute("SELECT data FROM graph ORDER BY id DESC LIMIT 1").fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="저장된 그래프가 없습니다.")
    data = json.loads(row["data"])

    nodes = {n["id"]: n for n in data["nodes"]}
    if from_id not in nodes:
        raise HTTPException(status_code=404, detail=f"출발 노드 '{from_id}' 없음")
    if to_id not in nodes:
        raise HTTPException(status_code=404, detail=f"도착 노드 '{to_id}' 없음")

    # 인접 리스트 구성 (무향 그래프, 가중치 = 유클리드 거리)
    adj: dict[str, list[tuple[str, float]]] = {nid: [] for nid in nodes}
    for e in data["edges"]:
        a, b = e["from"], e["to"]
        if a not in nodes or b not in nodes:
            continue
        dist = math.sqrt(
            (nodes[a]["x"] - nodes[b]["x"]) ** 2 +
            (nodes[a]["y"] - nodes[b]["y"]) ** 2 +
            (nodes[a]["z"] - nodes[b]["z"]) ** 2
        )
        adj[a].append((b, dist))
        adj[b].append((a, dist))

    def heuristic(a: str, b: str) -> float:
        return math.sqrt(
            (nodes[a]["x"] - nodes[b]["x"]) ** 2 +
            (nodes[a]["y"] - nodes[b]["y"]) ** 2 +
            (nodes[a]["z"] - nodes[b]["z"]) ** 2
        )

    # A* 탐색
    # heap: (f_score, g_score, node_id, path)
    heap: list[tuple[float, float, str, list[str]]] = [
        (heuristic(from_id, to_id), 0.0, from_id, [from_id])
    ]
    visited: set[str] = set()

    while heap:
        f, g, cur, path = heapq.heappop(heap)
        if cur in visited:
            continue
        visited.add(cur)
        if cur == to_id:
            return {"path": [nodes[nid] for nid in path]}
        for nxt, w in adj[cur]:
            if nxt not in visited:
                g_new = g + w
                heapq.heappush(heap, (g_new + heuristic(nxt, to_id), g_new, nxt, path + [nxt]))

    raise HTTPException(status_code=404, detail="경로를 찾을 수 없습니다.")

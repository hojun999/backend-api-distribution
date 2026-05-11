# Backend — PLY Navigator

## 현재 구현 상태

### 완료
- **백엔드** — `backend/main.py`
  - `POST /graph` : SQLite에 그래프 저장 (전체 교체 방식 — DELETE + INSERT)
  - `GET /graph` : 저장된 그래프 반환. 없으면 `{"nodes": [], "edges": []}` 반환
  - `GET /path?from=id&to=id` : A* 경로 탐색 (유클리드 3D 거리 가중치 + 휴리스틱). 경로 없으면 HTTP 404
  - CORS 전체 허용 (`allow_origins=["*"]`)

---

## 중요 결정사항

- **Node type**: `Literal["room", "waypoint", "start"]` — Pydantic으로 강제. 다른 값은 POST 시 422 반환
  - room: 길찾기 출발지/목적지
  - waypoint: 경로 중간 노드
  - start: 뷰어 보행 모드 진입 위치 (프론트에서 하나만 허용)
- **엣지 데이터**: JSON 키 `from`이 Python 예약어라 `Edge.__init__`에서 `dict`로 받아 처리. `from_` 필드명 사용
- **A* 경로**: `GET /path?from=<id>&to=<id>` → `{ "path": [{ id, name, type, x, y, z }, ...] }`. FastAPI `Query` alias로 `from` 예약어 처리
- **A* 가중치/휴리스틱**: 유클리드 3D 거리 (admissible). `import math, heapq` 사용
- **DB 구조**: 단일 테이블 `graph(id, data TEXT, updated_at)`. `data`는 전체 그래프 JSON 직렬화. 항상 최신 1행만 사용
- **실행 방법**: `py -m uvicorn main:app --reload --port 8000` (`backend/` 디렉토리에서 실행)

---

## 작업 로그

### 2026-04-16
**완료**
- 백엔드 기본 구조: FastAPI + SQLite, `POST /graph`, `GET /graph`
- A* 경로 탐색: `GET /path?from=id&to=id` 엔드포인트 추가

### 2026-04-18
**완료**
- **Node type에 `"start"` 추가** (`main.py`):
  - `Literal["room", "waypoint"]` → `Literal["room", "waypoint", "start"]`
  - 뷰어 보행 모드 진입 위치 지정용 타입

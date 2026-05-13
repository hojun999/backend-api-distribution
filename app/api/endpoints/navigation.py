import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.building import Building, Floor
from app.models.navigation import NavigationGraph
from app.schemas.navigation import (
    BuildingGraphsResponse,
    FloorGraphResponse,
    GraphPayload,
    PathResponse,
)
from app.services.pathfinding import find_path

router = APIRouter()


@router.put("/floors/{floor_id}/graph", response_model=FloorGraphResponse)
def save_floor_graph(
    floor_id: int,
    payload: GraphPayload,
    db: Session = Depends(get_db),
):
    floor = db.query(Floor).filter(Floor.id == floor_id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")

    graph = db.query(NavigationGraph).filter(NavigationGraph.floor_id == floor_id).first()
    data = payload.model_dump_json(by_alias=True)
    if graph:
        graph.data = data
    else:
        graph = NavigationGraph(floor_id=floor_id, data=data)
        db.add(graph)

    db.commit()
    db.refresh(graph)
    return _floor_graph_response(graph)


@router.get("/floors/{floor_id}/graph", response_model=FloorGraphResponse)
def get_floor_graph(floor_id: int, db: Session = Depends(get_db)):
    floor = db.query(Floor).filter(Floor.id == floor_id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")

    graph = db.query(NavigationGraph).filter(NavigationGraph.floor_id == floor_id).first()
    if graph is None:
        return FloorGraphResponse(floor_id=floor_id, graph=GraphPayload(nodes=[], edges=[]))
    return _floor_graph_response(graph)


@router.get("/buildings/{building_id}/graphs", response_model=BuildingGraphsResponse)
def get_building_graphs(building_id: int, db: Session = Depends(get_db)):
    building = db.query(Building).filter(Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    floor_ids = [floor.id for floor in building.floors]
    graphs = []
    if floor_ids:
        graphs = (
            db.query(NavigationGraph)
            .filter(NavigationGraph.floor_id.in_(floor_ids))
            .all()
        )

    graph_by_floor_id = {graph.floor_id: graph for graph in graphs}
    return BuildingGraphsResponse(
        building_id=building_id,
        floors=[
            _floor_graph_response(graph_by_floor_id[floor.id])
            if floor.id in graph_by_floor_id
            else FloorGraphResponse(floor_id=floor.id, graph=GraphPayload(nodes=[], edges=[]))
            for floor in building.floors
        ],
    )


@router.get("/floors/{floor_id}/path", response_model=PathResponse)
def get_floor_path(
    floor_id: int,
    from_id: str = Query(..., alias="from"),
    to_id: str = Query(..., alias="to"),
    db: Session = Depends(get_db),
):
    floor = db.query(Floor).filter(Floor.id == floor_id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")

    graph = db.query(NavigationGraph).filter(NavigationGraph.floor_id == floor_id).first()
    if graph is None:
        raise HTTPException(status_code=404, detail="Navigation graph not found")

    payload = _load_payload(graph)
    node_ids = {node.id for node in payload.nodes}
    if from_id not in node_ids:
        raise HTTPException(status_code=404, detail=f"Start node '{from_id}' not found")
    if to_id not in node_ids:
        raise HTTPException(status_code=404, detail=f"Destination node '{to_id}' not found")

    path = find_path(payload.nodes, payload.edges, from_id, to_id)
    if path is None:
        raise HTTPException(status_code=404, detail="Path not found")
    return PathResponse(floor_id=floor_id, path=path)


def _floor_graph_response(graph: NavigationGraph) -> FloorGraphResponse:
    return FloorGraphResponse(
        floor_id=graph.floor_id,
        graph=_load_payload(graph),
        updated_at=graph.updated_at,
    )


def _load_payload(graph: NavigationGraph) -> GraphPayload:
    return GraphPayload.model_validate(_normalize_legacy_node_types(json.loads(graph.data)))


def _normalize_legacy_node_types(data: dict) -> dict:
    for node in data.get("nodes", []):
        if node.get("type") == "room":
            node["type"] = "door"
    return data

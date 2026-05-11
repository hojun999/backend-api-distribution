from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Node(BaseModel):
    id: str
    name: str
    type: Literal["door", "waypoint", "start", "destination"]
    x: float
    y: float
    z: float


class Edge(BaseModel):
    id: str
    from_: str = Field(alias="from")
    to: str

    model_config = ConfigDict(populate_by_name=True)


class GraphPayload(BaseModel):
    nodes: list[Node]
    edges: list[Edge]


class FloorGraphResponse(BaseModel):
    floor_id: int
    graph: GraphPayload
    updated_at: datetime | None = None


class BuildingGraphsResponse(BaseModel):
    building_id: int
    floors: list[FloorGraphResponse]


class PathResponse(BaseModel):
    floor_id: int
    path: list[Node]

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.building import Building, Floor
from app.schemas.building import (
    BuildingCreate,
    BuildingResponse,
    BuildingUpdate,
    FloorCreate,
    FloorResponse,
    FloorUpdate,
)

router = APIRouter()


@router.post("/buildings", response_model=BuildingResponse)
def create_building(data: BuildingCreate, db: Session = Depends(get_db)):
    building = Building(**data.model_dump())
    db.add(building)
    db.commit()
    db.refresh(building)
    return building


@router.get("/buildings", response_model=List[BuildingResponse])
def get_buildings(db: Session = Depends(get_db)):
    return db.query(Building).all()


@router.get("/buildings/{building_id}", response_model=BuildingResponse)
def get_building(building_id: int, db: Session = Depends(get_db)):
    building = db.query(Building).filter(Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return building


@router.patch("/buildings/{building_id}", response_model=BuildingResponse)
def update_building(
    building_id: int,
    data: BuildingUpdate,
    db: Session = Depends(get_db),
):
    building = db.query(Building).filter(Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(building, key, value)
    db.commit()
    db.refresh(building)
    return building


@router.delete("/buildings/{building_id}")
def delete_building(building_id: int, db: Session = Depends(get_db)):
    building = db.query(Building).filter(Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    db.delete(building)
    db.commit()
    return {"detail": "Deleted"}


@router.post("/floors", response_model=FloorResponse)
def create_floor(data: FloorCreate, db: Session = Depends(get_db)):
    floor = Floor(**data.model_dump())
    db.add(floor)
    db.commit()
    db.refresh(floor)
    return floor


@router.get("/floors", response_model=List[FloorResponse])
def get_floors(building_id: int, db: Session = Depends(get_db)):
    return db.query(Floor).filter(Floor.building_id == building_id).all()


@router.get("/floors/{floor_id}", response_model=FloorResponse)
def get_floor(floor_id: int, db: Session = Depends(get_db)):
    floor = db.query(Floor).filter(Floor.id == floor_id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    return floor


@router.patch("/floors/{floor_id}", response_model=FloorResponse)
def update_floor(
    floor_id: int,
    data: FloorUpdate,
    db: Session = Depends(get_db),
):
    floor = db.query(Floor).filter(Floor.id == floor_id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(floor, key, value)
    db.commit()
    db.refresh(floor)
    return floor


@router.delete("/floors/{floor_id}")
def delete_floor(floor_id: int, db: Session = Depends(get_db)):
    floor = db.query(Floor).filter(Floor.id == floor_id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    db.delete(floor)
    db.commit()
    return {"detail": "Deleted"}

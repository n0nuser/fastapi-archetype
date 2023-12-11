import datetime

from fastapi import APIRouter
from fastapi.responses import Response
from sqlalchemy_utils import create_database

from src.api.schemas.error_message import ErrorMessage
from src.db.models import (
    Absence,
    Address,
    Base,
    Booking,
    Office,
    Section,
    StatusDay,
    Workstation,
)
from src.db.session import Session, engine

router = APIRouter()


@router.post(
    "/create-db",
    responses={
        201: {"description": "Created."},
        500: {"model": ErrorMessage, "description": "Internal Server Error."},
    },
    tags=["DB"],
    summary="Create database.",
)
async def create_db() -> None:
    create_database(engine.url)
    return Response(status_code=201)


@router.post(
    "/drop-tables",
    responses={
        204: {"description": "No Content."},
        500: {"model": ErrorMessage, "description": "Internal Server Error."},
    },
    tags=["DB"],
    summary="Drop Tables.",
)
async def drop_tables() -> None:
    with engine.begin() as conn:
        # always drop and create test db tables between tests session
        Base.metadata.drop_all(bind=conn)
    return Response(status_code=204)


@router.post(
    "/create-tables",
    responses={
        201: {"description": "Created."},
        500: {"model": ErrorMessage, "description": "Internal Server Error."},
    },
    tags=["DB"],
    summary="Create Tables.",
)
async def create_tables() -> None:
    with engine.begin() as conn:
        # always drop and create test db tables between tests session
        Base.metadata.create_all(bind=conn)
    return Response(status_code=201)


@router.post(
    "/populate-tables",
    responses={
        201: {"description": "Created."},
        500: {"model": ErrorMessage, "description": "Internal Server Error."},
    },
    tags=["DB"],
    summary="Populate Tables.",
)
async def populate_tables() -> None:
    with Session() as session:
        for i in range(5):
            objects = [
                Office(name="Axpe Consulting S.L."),
                Address(
                    line="C/Toro, nº71",
                    street_name="C/Toro",
                    building_number="nº 71",
                    stair="1",
                    floor=1,
                    door_number="1A",
                    postal_code="37002",
                    province="Salamanca",
                    country="ES",
                    office_id=i + 1,
                ),
                Section(name="Principal", physical=True, office_id=i + 1),
                Workstation(
                    name="Mesa 1",
                    position=1,
                    x_coord=3.5,
                    y_coord=5.5,
                    rotation=360,
                    section_id=i + 1,
                    locked=True,
                ),
                StatusDay(name="Mañana"),
                Booking(
                    workstation_id=i + 1,
                    employee_id=1,
                    status_day_id=1,
                    start_date=datetime.date.today(),
                    end_date=datetime.date.today() + datetime.timedelta(days=4),
                    permanent=True,
                    deleted_on=None,
                ),
                Absence(
                    employee_id=1,
                    status_day_id=1,
                    start_date=datetime.date.today(),
                    end_date=datetime.date.today() + datetime.timedelta(days=1),
                    comment="Ir al médico.",
                    deleted_on=None,
                    cause="Enfermedad",
                ),
            ]
            for element in objects:
                session.add(element)
        session.commit()
    return Response(status_code=201)

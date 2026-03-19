"""
Minimal smoke test — verifies the FastAPI app imports and the Pydantic
schemas parse correctly without needing a database connection.
"""

import uuid
from decimal import Decimal

import pytest

from app.schemas.fleet import VehicleCreate
from app.schemas.driver import DriverCreate
from app.schemas.route import RouteCreate, RouteRead


def test_vehicle_create_schema_valid():
    """VehicleCreate accepts valid Singapore vehicle data."""
    vehicle = VehicleCreate(
        tenant_id=uuid.uuid4(),
        license_plate="SBA1234A",
        make="Isuzu",
        model="N-Series NMR85H",
        year=2022,
        vin="JNKBANT15Z0000001",
        status="active",
    )
    assert vehicle.license_plate == "SBA1234A"
    assert vehicle.make == "Isuzu"
    assert vehicle.year == 2022


def test_driver_create_schema_defaults():
    """DriverCreate applies 'novice' as the default experience_level."""
    driver = DriverCreate(
        tenant_id=uuid.uuid4(),
        first_name="Ravi",
        last_name="Kumar",
        email="ravi@fleet.sg",
        license_number="SG-CDL-2019-00421",
    )
    assert driver.experience_level == "novice"
    assert driver.status == "active"
    assert driver.vehicle_id is None


def test_route_create_schema_defaults():
    """RouteCreate defaults to 'highway' route_type."""
    route = RouteCreate(
        tenant_id=uuid.uuid4(),
        name="Tuas → Tampines",
        start_location="Tuas Hub",
        end_location="Tampines DC",
        distance_km=Decimal("42.5"),
    )
    assert route.route_type == "highway"


def test_vehicle_year_boundary():
    """VehicleCreate rejects years outside the valid range."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        VehicleCreate(
            tenant_id=uuid.uuid4(),
            license_plate="SBA0000A",
            make="Test",
            model="Model",
            year=1989,  # Below minimum of 1990
            status="active",
        )

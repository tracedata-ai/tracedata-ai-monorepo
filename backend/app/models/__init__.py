"""
TraceData Backend — Models package.

Importing all models here ensures SQLAlchemy's metadata is populated
when `Base.metadata.create_all()` is called in main.py.

WHY THIS MATTERS: SQLAlchemy only knows about a table if the model class
has been imported. Without this file, `create_all()` would silently create
zero tables even though the model files exist.
"""

from app.models.driver import Driver
from app.models.fleet import Vehicle
from app.models.issue import Issue
from app.models.maintenance import Maintenance
from app.models.route import Route
from app.models.tenant import Tenant
from app.models.trip import Trip

__all__ = ["Vehicle", "Driver", "Route", "Trip", "Issue", "Maintenance", "Tenant"]

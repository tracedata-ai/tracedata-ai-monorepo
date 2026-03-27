"""
TraceData Backend — Models package.

Importing all models here ensures SQLAlchemy's metadata is populated
when `Base.metadata.create_all()` is called in main.py.

WHY THIS MATTERS: SQLAlchemy only knows about a table if the model class
has been imported. Without this file, `create_all()` would silently create
zero tables even though the model files exist.
"""

from api.models.driver import Driver
from api.models.fleet import Vehicle
from api.models.issue import Issue
from api.models.maintenance import Maintenance
from api.models.route import Route
from api.models.tenant import Tenant
from api.models.trip import Trip

__all__ = ["Vehicle", "Driver", "Route", "Trip", "Issue", "Maintenance", "Tenant"]

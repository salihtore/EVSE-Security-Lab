# src/api/routes/cp.py

from fastapi import APIRouter
from src.api.services.cp_state import cp_state

router = APIRouter(prefix="/cp", tags=["ChargePoints"])


@router.get("/status")
def all_status():
    """
    Dashboard'ın çağırdığı endpoint.
    Örnek çıktı:
    {
      "CP_EMIN": { "status": "Charging" }
    }
    """
    return cp_state.get_all()

from fastapi import APIRouter, HTTPException

from app.domain.farmer.repository import list_farmers, get_farmer_by_id


router = APIRouter(prefix="/v1/farmers", tags=["Farmers"])


@router.get("", operation_id="list_farmers")
def get_farmers():
    farmers = list_farmers()

    return {
        "count": len(farmers),
        "farmers": farmers
    }


@router.get("/{farmer_id}", operation_id="get_farmer")
def get_farmer(farmer_id: str):
    farmer = get_farmer_by_id(farmer_id)

    if not farmer:
        raise HTTPException(status_code=404, detail=f"Farmer {farmer_id} not found")

    return farmer

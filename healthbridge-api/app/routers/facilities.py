"""
Facilities router — nearby health facilities.

#11  GET /facilities/nearby  —  Get nearby PHC/hospital from Google Maps Places API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
import httpx

from app.config import settings
from app.models.asha_worker import ASHAWorker
from app.routers.auth import get_current_worker

router = APIRouter(prefix="/facilities", tags=["Facilities"])


@router.get("/nearby")
async def find_nearby_facilities(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius: int = Query(5000, description="Search radius in meters (default 5km)"),
    facility_type: str = Query("hospital", description="hospital|pharmacy|doctor"),
    worker: ASHAWorker = Depends(get_current_worker),
):
    """Find nearby health facilities using Google Maps Places API.

    Returns up to 10 facilities within the specified radius.
    """
    if not settings.google_maps_api_key:
        raise HTTPException(
            status_code=503,
            detail="Google Maps API key not configured",
        )

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": facility_type,
        "keyword": "health hospital clinic PHC",
        "key": settings.google_maps_api_key,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, params=params)
        data = response.json()

    if data.get("status") != "OK":
        return {"facilities": [], "count": 0, "message": "No facilities found nearby"}

    facilities = []
    for place in data.get("results", [])[:10]:
        facilities.append({
            "name": place.get("name"),
            "address": place.get("vicinity"),
            "lat": place["geometry"]["location"]["lat"],
            "lng": place["geometry"]["location"]["lng"],
            "rating": place.get("rating"),
            "open_now": place.get("opening_hours", {}).get("open_now"),
            "place_id": place.get("place_id"),
        })

    return {"facilities": facilities, "count": len(facilities)}

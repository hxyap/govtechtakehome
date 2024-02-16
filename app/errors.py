from .models import APIError
from typing import Optional

def InvalidParametersError(request_id: Optional[str] = None):
    return APIError(
        code=400,
        message="Invalid parameters provided",
        request={"id": request_id} if request_id else None,
        details={"message": "Your conversation id was incorrect."}
    )
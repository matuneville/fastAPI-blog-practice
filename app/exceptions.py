from fastapi import status, HTTPException

def raise_not_found_except(detail: str = "Resource not found"):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

def raise_forbidden_except(detail: str = "Not authorized to perform this action"):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

def raise_bad_request_except(detail: str = "Invalid request"):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

def raise_unauthorized_except(detail: str = "Incorrect username or password"):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers={"WWW-Authenticate": "Bearer"},)

def raise_conflict_except(detail: str = "Conflict occurred"):
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
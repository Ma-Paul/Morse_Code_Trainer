from fastapi import Header, HTTPException

API_KEY = "MORSE_API_SFZ_FIRSTTEST"


def require_api_key(x_api_key: str = Header(default=None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

from pydantic import BaseModel


class SecurityContext(BaseModel):
    token: str
    intent_id: str
    hmac_sig: str

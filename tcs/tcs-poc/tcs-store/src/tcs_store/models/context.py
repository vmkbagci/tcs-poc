"""Context model for lifecycle tracing."""

from pydantic import BaseModel, Field, field_validator


class Context(BaseModel):
    """Context metadata for lifecycle tracing."""
    
    user: str = Field(..., min_length=1, description="User ID or service account making the request")
    agent: str = Field(..., min_length=1, description="Application or service identifier")
    action: str = Field(..., min_length=1, description="Operation being performed")
    intent: str = Field(..., min_length=1, description="Business reason or workflow step")
    
    @field_validator("user", "agent", "action", "intent")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Validate that fields are non-empty strings."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user": "trader_123",
                    "agent": "trading_platform",
                    "action": "save_new",
                    "intent": "new_trade_booking"
                }
            ]
        }
    }

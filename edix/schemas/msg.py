"""
Message response schemas for API endpoints.
"""
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class Msg(BaseModel):
    """
    Generic message response schema.
    
    Used for simple API responses that need to return a message.
    """
    message: str
    details: Optional[str] = None
    code: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Operation completed successfully",
                "details": "Additional information about the operation",
                "code": "SUCCESS"
            }
        }
    )


class ErrorMsg(Msg):
    """
    Error message response schema.
    
    Extends Msg with error-specific fields.
    """
    error_type: Optional[str] = None
    error_code: Optional[int] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "An error occurred",
                "details": "Detailed error description",
                "code": "ERROR",
                "error_type": "ValidationError",
                "error_code": 400
            }
        }
    )


class SuccessMsg(Msg):
    """
    Success message response schema.
    
    Extends Msg with success-specific fields.
    """
    data: Optional[Any] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Operation completed successfully",
                "details": "Resource created successfully",
                "code": "SUCCESS",
                "data": {"id": 123, "name": "Example"}
            }
        }
    )

from pydantic import BaseModel, Field
from beanie import Document
from typing import Optional, Dict, Any, List
from enum import Enum
from uuid import uuid4, UUID

class APIError(BaseModel):
    code: int = Field(..., description="API Error code associated with the error")
    message: str = Field(..., description="Error message associated with the error")
    request: Optional[Dict[str, Any]] = Field(None, description="Request details associated with the error")
    details: Optional[Dict[str, Any]] = Field(None, description="Other details associated with the error")

class InvalidParametersError(APIError):
    code: int = Field(400, description="API Error code associated with the error")
    message: str = Field("Invalid parameters provided", description="Error message associated with the error")
class InternalServerError(APIError):
    code: int = Field(500, description="API Error code associated with the error")
    message: str = Field("Internal server error", description="Error message associated with the error")

class NotFoundError(APIError):
    code: int = Field(404, description="API Error code associated with the error")
    message: str = Field("Specified resource(s) was not found", description="Error message associated with the error")

class InvalidCreationError(APIError):
    code: int = Field(422, description="API Error code associated with the error")
    message: str = Field("Unable to create resource due to errors", description="Error message associated with the error")
class QueryRoleType(str, Enum):
    system = 'system'
    user = 'user'
    assistant = 'assistant'
    function = 'function'

class Prompt(BaseModel):
    role: QueryRoleType = Field(..., description="Chat roles for each individual message")
    content: str = Field(..., description="This is the prompt content of the message", format="text")

class Conversation(Document):
    id: UUID = Field(default_factory=uuid4, description="ID of the conversation", alias="_id")
    name: str = Field(..., description="Title of the conversation", max_length=200)
    params: Dict[str, Any] = Field(..., description="Parameter dictionary for overriding defaults prescribed by the AI Model")
    tokens: Optional[int] = Field(None, description="Total number of tokens consumed in this entire Chat", ge=0, readOnly=True)

class ConversationFull(Conversation):
    messages: Optional[List[Prompt]] = Field(..., description="Chat messages to be included")

class ConversationPOST(BaseModel):
    name: str = Field(..., description="Title of the conversation", max_length=200)
    params: Dict[str, Any] = Field(default_factory=dict, description="Parameter dictionary for overriding defaults prescribed by the AI Model")

class ConversationPUT(BaseModel):
    name: Optional[str] = Field(None, description="Title of the conversation", max_length=200)
    params: Optional[Dict[str, Any]] = Field(None, description="Parameter dictionary for overriding defaults prescribed by the AI Model")

class CreatedResponse(BaseModel):
    id: UUID = Field(..., description="Generated resource ID")

class DeletedResponse(BaseModel):
    detail: str = Field("Successfully updated specified resource", description="Successfully updated specified resource")

class UpdatedResponse(BaseModel):
    detail: str = Field("Successfully deleted specified resource(s)", description="Successfully deleted specified resource(s)")

class ConversationPOST(BaseModel):
    name: str = Field(..., description="Title of the conversation", max_length=200)
    params: Dict[str, Any] = Field(..., description="Parameter dictionary for overriding defaults prescribed by the AI Model")


    
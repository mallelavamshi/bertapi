from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class TextInput(BaseModel):
    text: str = Field(..., description="Legal document text to process")
    summary_length: Optional[int] = Field(5, description="Number of sentences in summary")
    num_facts: Optional[int] = Field(10, description="Number of important facts to extract")

class EntityResponse(BaseModel):
    case_numbers: List[str]
    courts: List[str]
    citations: List[str]
    statutes: List[str]
    plaintiffs: List[str]
    defendants: List[str]
    judges: List[str]
    attorneys: List[str]
    dates: List[str]
    locations: List[str]
    organizations: List[str]
    case_type: Optional[str]
    jurisdiction: Optional[str]

class ProcessResponse(BaseModel):
    status: str
    entities: EntityResponse
    summary: str
    important_facts: List[str]
    processing_time: float

class HealthResponse(BaseModel):
    status: str
    version: str
    model_loaded: bool

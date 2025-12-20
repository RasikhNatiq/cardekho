# schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class FilterRange(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None

class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query for searching cars")
    max_results: Optional[int] = Field(100, description="Maximum number of results to return")

class QueryResponse(BaseModel):
    query: str
    applied_filters: Dict[str, Any]
    non_matched_columns: List[str]
    total_results: int
    returned_results: int
    timestamp: str
    results: List[Dict[str, Any]]

class DatasetInfo(BaseModel):
    total_records: int
    columns: List[str]
    column_types: Dict[str, str]
    color_column: Optional[str]
    sample_records: List[Dict[str, Any]]

class HealthCheck(BaseModel):
    status: str
    timestamp: str
    dataset_loaded: bool
    openrouter_connected: bool
    total_cars: Optional[int] = None
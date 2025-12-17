from dataclasses import dataclass
from typing import Optional



@dataclass
class Config:
    openapi_path: Optional[str] = None
    test_cases_path: Optional[str] = None
    swagger_path: Optional[str] = None
    report_path: Optional[str] = None
    ai_model: Optional[str] = None
    openAi_api_key: Optional[str] = None

from typing import Literal
from pydantic import BaseModel, Field

class DriverImpact(BaseModel):
    area:str=Field(min_length=1,max_length=160)
    direction:Literal['strengthened','weakened','unchanged','uncertain']
    magnitude:Literal['low','medium','high']
    confidence:Literal['low','medium','high']
    reason:str=Field(min_length=1,max_length=700)

class ValuationImpact(BaseModel):
    target:Literal['base_metric','multiple']
    direction:Literal['up','down','unchanged','uncertain']
    magnitude:Literal['low','medium','high']
    confidence:Literal['low','medium','high']
    reason:str=Field(min_length=1,max_length=500)

class TargetedResearchUpdate(BaseModel):
    summary:str=Field(min_length=1,max_length=2500)
    driver_impacts:list[DriverImpact]=Field(default_factory=list,max_length=6)
    valuation_implications:list[ValuationImpact]=Field(default_factory=list,max_length=2)
    full_review_recommended:bool=False
    full_review_reason:str|None=Field(default=None,max_length=700)

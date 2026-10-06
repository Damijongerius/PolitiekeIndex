from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Quote(BaseModel):
    page: int
    filename: str
    text: str

class PartyStance(BaseModel):
    party_id: str
    party_name: str
    party_color: str
    score: Optional[float] = None
    score_label: str
    is_unknown: bool = False
    explanation: str
    quotes: List[Quote] = []

class Dimensions(BaseModel):
    statement: str
    left_right_orientation: float
    prog_cons_orientation: float
    lr_label: str
    pc_label: str
    economic_explanation: Optional[str] = None
    cultural_explanation: Optional[str] = None

class StatementEvaluationResponse(BaseModel):
    statement: str
    dimensions: Dimensions
    party_stances: List[PartyStance]

class StatementRequest(BaseModel):
    statement: str

class CompassParty(BaseModel):
    id: str
    name: str
    fullName: str
    color: str
    textColor: str
    x: float  # -10 (Links) to +10 (Rechts)
    y: float  # -10 (Conservatief) to +10 (Progressief)
    seats: int
    inParliament: bool
    summary: str

class CompassResponse(BaseModel):
    parties: List[CompassParty]
    user_statement_point: Optional[Dict[str, Any]] = None

class ThemeDetail(BaseModel):
    title: str
    score: float
    label: str
    summary: str
    quotes: List[Quote] = []

class Kamerlid(BaseModel):
    name: str
    role: str
    link: Optional[str] = None
    photo: Optional[str] = None

class FractieInfo(BaseModel):
    id: str
    name: str
    seats: int
    leader: Optional[str] = None
    leaderRole: Optional[str] = None
    leaderPhoto: Optional[str] = None
    logo: Optional[str] = None
    detailUrl: str
    fullTitle: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    members: List[Kamerlid] = []
    totalMembers: Optional[int] = None

class TweedeKamerResponse(BaseModel):
    lastUpdated: str
    sourceUrl: str
    totalSeats: int
    fractiesCount: int
    fracties: List[FractieInfo]

class PartySummary(BaseModel):
    id: str
    name: str
    fullName: str
    leader: str
    seats: int
    inParliament: bool
    orientation: str
    color: str
    textColor: str
    pdfAvailable: bool
    coverUrl: str
    pdfUrl: str
    pageCount: Optional[int] = None
    compass: Dict[str, float]
    shortDescription: str
    tkData: Optional[FractieInfo] = None

class PartyDetail(PartySummary):
    visionSummary: str
    themes: Dict[str, ThemeDetail] = {}


class CompareRequest(BaseModel):
    party_ids: List[str]
    theme_keys: Optional[List[str]] = None

class ThemeComparisonItem(BaseModel):
    theme_key: str
    theme_name: str
    stances: Dict[str, ThemeDetail]  # party_id -> ThemeDetail

class CompareResponse(BaseModel):
    parties: List[PartySummary]
    themes: List[ThemeComparisonItem]


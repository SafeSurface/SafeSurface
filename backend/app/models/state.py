from typing import Annotated, TypedDict, List, Dict
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AssetState(BaseModel):
    ip_or_domain: str
    ports: List[int] = []
    services: Dict[int, str] = {}
    vulnerabilities: List[str] = []

class AttackTree(BaseModel):
    pending_targets: List[str] = Field(default_factory=list)
    exploited_targets: List[str] = Field(default_factory=list)
    blocked_targets: List[str] = Field(default_factory=list)

class SafeSurfaceState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]
    assets: Dict[str, AssetState]
    attack_tree: AttackTree
    current_focus: str
    next_step: str

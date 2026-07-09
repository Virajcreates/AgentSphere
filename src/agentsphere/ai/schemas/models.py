from pydantic import BaseModel, Field


class ModelCapabilities(BaseModel):
    streaming: bool = True
    vision: bool = False
    reasoning: bool = False
    json_mode: bool = False
    tool_calling: bool = False
    embeddings: bool = False


class ModelCosts(BaseModel):
    input_cost_per_1m: float = 0.0
    output_cost_per_1m: float = 0.0


class ModelInfo(BaseModel):
    model_id: str
    provider: str
    display_name: str
    context_window: int = 4096
    capabilities: ModelCapabilities = Field(default_factory=ModelCapabilities)
    costs: ModelCosts = Field(default_factory=ModelCosts)
    is_healthy: bool = True
    average_latency: float = 0.0
    success_rate: float = 1.0

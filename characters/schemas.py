from pydantic import BaseModel, Field


class EvilnessClassification(BaseModel):
    """Pydantic model for structured evilness classification output."""

    is_evil: bool = Field(description="Whether the character is classified as evil")
    evilness_score: int = Field(
        ge=0, le=100, description="Evilness score from 0 (good) to 100 (evil)"
    )
    evilness_explanation: str = Field(
        description="Detailed explanation of the evilness classification and score"
    )

from typing import List, Dict, Any

from django.conf import settings
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from .schemas import EvilnessClassification


class BiographyGenerator:
    """Service for generating character biographies using AI."""

    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        self.llm = ChatOpenAI(
            model="gpt-5-nano",
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7
        )

    def generate_biography(self, character_data: Dict[str, Any]) -> str:
        """Generate a short biography for a character"""
        name = character_data.get("name", "Unknown Character")
        species = character_data.get("species", "Unknown Species")
        homeworld = character_data.get("homeworld", "Unknown Homeworld")
        affiliations = ", ".join(character_data.get("affiliations", []))

        prompt = f"""
Write a short, engaging biography (2-3 sentences) for the Star Wars character {name}.

Here are some known details:
- Species: {species}
- Homeworld: {homeworld}
- Affiliations: {", ".join(affiliations) if affiliations else "None known"}

Keep it concise, interesting, and true to the Star Wars universe. Focus on their role and significance.
"""

        try:
            message = HumanMessage(content=prompt)
            response = self.llm.invoke([message])
            return response.content.strip()
        except Exception as e:
            print(f"Error generating biography: {e}")
            # Return a fallback message if AI generation fails
            return f"A {species} from {homeworld}, {name} is a character of interest."


class EvilnessClassifier:
    """Service for classifying character evilness using AI with structured output."""

    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        self.llm = ChatOpenAI(
            model="gpt-5-mini", api_key=settings.OPENAI_API_KEY, temperature=0.3
        )

    def classify_evilness(
        self, character_data: Dict[str, Any], master_names: List[str] = []
    ) -> EvilnessClassification:
        """Classify a character's evilness with structured output."""
        name = character_data.get("name", "Unknown Character")
        species = character_data.get("species", "Unknown Species")
        homeworld = character_data.get("homeworld", "Unknown Homeworld")
        affiliations = character_data.get("affiliations", [])

        prompt = f"""
Analyze the Star Wars character {name} and classify their evilness based on some rules

Character Details:
- Name: {name}
- Species: {species}
- Homeworld: {homeworld}
- Affiliations: {", ".join(affiliations) if affiliations else "None known"}
- Masters: {", ".join(master_names) if master_names else "None known"}

A character is considered evil if:
- They have 'Darth' or 'Sith' in their name
- They have at least one affiliation that mentions 'Darth' or 'Sith'
- They have at least one master with 'Darth' in their name

The evilness score should be determined on how evil the character is, with 0 being pure good and 100 being pure evil. You can calculate the score based on the rules above. If a character has all of the above they should get a very high score, if they have none of the above they should get a very low score. Other factors of the character itself should have a very small impact on the score.

Explain short in 1-2 sentences why you classified it like that. Never say "based on the provided criteria" but rather mention the specific criteria because the user does not know what the criteria are.

Provide:
1. is_evil: True if evil, False if not
2. evilness_score: 0-100 scale (0 = pure good, 100 = pure evil)
3. evilness_explanation: Detailed reasoning for the classification
"""

        try:
            structured_llm = self.llm.with_structured_output(EvilnessClassification)
            message = HumanMessage(content=prompt)
            response = structured_llm.invoke([message])
            return response
        except Exception as e:
            print(f"Error classifying evilness: {e}")
            # Return fallback classification
            return EvilnessClassification(
                is_evil=False,
                evilness_score=0,
                evilness_explanation=f"Unable to classify {name}. Defaulted to good.",
            )

from typing import List, Dict, Any

from django.conf import settings
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


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
- Affiliations: {', '.join(affiliations) if affiliations else 'None known'}

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




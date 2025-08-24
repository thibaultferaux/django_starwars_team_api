from typing import List, Dict, Any

from django.conf import settings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage
from sklearn.metrics.pairwise import cosine_similarity

from .schemas import EvilnessClassification
from .models import Character


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


class SemanticSearchService:
    """Service for semantic search using embeddings"""
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=settings.OPENAI_API_KEY
        )

    def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding vector for the given text"""
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []

    def search_characters(self, query: str, limit: int = 10) -> List[Character]:
        """Perform semantic search on characters"""
        query_embedding = self.generate_embedding(query)
        if not query_embedding:
            return []

        # Get characters with embedding
        characters = Character.objects.filter(description_embedding__isnull=False)
        results = []
        for character in characters:
            if character.description_embedding:
                try:
                    char_embedding = character.description_embedding
                    similarity = cosine_similarity(
                        [query_embedding], [char_embedding.vector]
                    )[0][0]
                    results.append((character, similarity))
                except Exception as e:
                    print(f"Error calculating similarity for {character.name}: {e}")
                    continue

        # Sort by similarity and limit results
        results.sort(key=lambda x: x[1], reverse=True)
        return [char for char, _ in results[:limit]]

    def update_character_embedding(self, character: Character):
        """Update the character's embedding based on their description"""
        description = character.get_description_for_embeddings()
        embedding_vector = self.generate_embedding(description)
        if embedding_vector:
            character.description_embedding = embedding_vector
            character.save(update_fields=["description_embedding"])
        

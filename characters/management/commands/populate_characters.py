import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction

from characters.models import Character, Master
from characters.services import BiographyGenerator, EvilnessClassifier, SemanticSearchService


class Command(BaseCommand):
    help = "Populate the database with Star Wars characters from the external API."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-ai",
            action="store_true",
            help="Skip AI-generated content (character properties and embeddings).",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limit the number of characters to process",
        )
        parser.add_argument(
            "--max-workers",
            type=int,
            default=8,
            help="Maximum number of concurrent workers",
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting to populate characters...")

        max_workers = options["max_workers"]

        try:
            # Fetch data from external API
            response = requests.get(
                settings.STARWARS_API_URL, timeout=30
            )  # Wait max 30 seconds for a response
            response.raise_for_status()
            characters_data = response.json()

            self.stdout.write(
                f"Fetched {len(characters_data)} characters from the API."
            )

            # Limit the number of characters if specified
            if options["limit"]:
                characters_data = characters_data[: options["limit"]]
                self.stdout.write(
                    f"Processing first {len(characters_data)} characters."
                )

            biography_generator = None
            evilness_classifier = None
            search_service = None

            if not options["skip_ai"]:
                try:
                    if settings.OPENAI_API_KEY:
                        biography_generator = BiographyGenerator()
                        evilness_classifier = EvilnessClassifier()
                        search_service = SemanticSearchService()
                        self.stdout.write("AI services initialized.")
                    else:
                        self.stderr.write(
                            "OpenAI API key is not set. Skipping AI-generated content."
                        )
                except Exception as e:
                    self.stderr.write(
                        f"Failed to initialize AI services: {e}."
                    )

            # Process all characters concurrently
            self.stdout.write(f"Processing {len(characters_data)} characters with {max_workers} workers...")

            total_created, total_updated = self._process_characters_concurrent(
                characters_data, biography_generator, evilness_classifier,
                search_service, max_workers
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully processed {total_created + total_updated} characters "
                    f"(created {total_created}, updated {total_updated})."
                )
            )

        except requests.RequestException as e:
            self.stderr.write(f"Error fetching data from API: {e}")
            return
        except Exception as e:
            self.stderr.write(f"Unexpected error: {e}")
            return

    def _process_characters_concurrent(self, characters_data, biography_generator=None,
                                     evilness_classifier=None, search_service=None, max_workers=4):
        """Process all characters concurrently using ThreadPoolExecutor."""
        created_count = 0
        updated_count = 0
        total_characters = len(characters_data)
        processed_count = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all character processing tasks
            future_to_char = {
                executor.submit(
                    self._process_character,
                    char_data, biography_generator, evilness_classifier, search_service
                ): char_data
                for char_data in characters_data
            }

            # Process completed tasks as they finish
            for future in as_completed(future_to_char):
                char_data = future_to_char[future]
                processed_count += 1

                try:
                    character, created = future.result()
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                    # Progress update every 10 characters or at the end
                    if processed_count % 10 == 0 or processed_count == total_characters:
                        self.stdout.write(
                            f"Progress: {processed_count}/{total_characters} characters processed "
                            f"({created_count} created, {updated_count} updated)"
                        )

                except Exception as e:
                    self.stderr.write(
                        f"Error processing character {char_data.get('name', 'unknown')}: {e}"
                    )
                    continue

        return created_count, updated_count

    @transaction.atomic
    def _process_character(self, char_data, biography_generator=None, evilness_classifier=None, search_service=None):
        """Process a single character from the API data."""

        # Get or create character
        character, created = Character.objects.update_or_create(
            id=char_data["id"],
            defaults={
                "name": char_data.get("name"),
                "height": self._safe_float(char_data.get("height")),
                "mass": self._safe_float(char_data.get("mass")),
                "gender": char_data.get("gender"),
                "homeworld": char_data.get("homeworld"),
                "species": char_data.get("species"),
                "image_url": char_data.get("image"),
                "affiliations_data": char_data.get("affiliations", []),
            },
        )

        # Process masters
        masters_data = char_data.get("masters", [])
        self._process_masters(character, masters_data)

        # Classify evilness
        if evilness_classifier and not character.is_evil:
            masters_names = [
                master.master_name for master in Master.objects.filter(character=character)
            ]
            try:
                evilness_result = evilness_classifier.classify_evilness(char_data, masters_names)
                # Update character with evilness classification
                character.is_evil = evilness_result.is_evil
                character.evilness_score = evilness_result.evilness_score
                character.evilness_explanation = evilness_result.evilness_explanation
            except Exception as e:
                self.stdout.write(f"Failed to classify evilness for {character.name}: {e}")

        # Generate biography if AI services are available
        if biography_generator and not character.biography:
            try:
                character.biography = biography_generator.generate_biography(char_data)
            except Exception as e:
                self.stdout.write(f"Failed to generate biography for {character.name}: {e}")

        # Save the character
        character.save()

        # Generate embeddings for semantic search
        if search_service:
            try:
                search_service.update_character_embedding(character)
            except Exception as e:
                self.stdout.write(
                    f"Failed to generate embedding for {character.name}: {e}"
                )

        return character, created

    def _process_masters(self, character, masters_data):
        """Process masters data for a character."""
        if isinstance(masters_data, str):
            # If masters_data is a string, treat it as a single master
            masters_data = [masters_data]

        if masters_data:
            # Clean and prepare master names
            new_master_names = {
                name.strip() for name in masters_data if name and name.strip()
            }

            if new_master_names:
                # Get existing masters for this character
                existing_master_names = set(
                    Master.objects.filter(character=character).values_list(
                        "master_name", flat=True
                    )
                )

                # Determine which masters to add and remove
                masters_to_add = new_master_names - existing_master_names
                masters_to_remove = existing_master_names - new_master_names

                # Remove masters that are no longer needed
                if masters_to_remove:
                    Master.objects.filter(
                        character=character, master_name__in=masters_to_remove
                    ).delete()

                # Add new masters only
                if masters_to_add:
                    Master.objects.bulk_create(
                        [
                            Master(character=character, master_name=name)
                            for name in masters_to_add
                        ]
                    )

        else:
            # If no masters data, ensure no masters exist for this character
            Master.objects.filter(character=character).delete()

    def _safe_float(self, value):
        """Safely convert value to float"""
        if value is None or value == "unknown" or value == "":
            return None
        try:
            # Handle comma as decimal separator
            if isinstance(value, str):
                value = value.replace(",", ".")
            return float(value)
        except (ValueError, TypeError):
            return None

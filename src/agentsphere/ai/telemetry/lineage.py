import uuid
from datetime import datetime
from typing import Any


class PromptLineageTracker:
    def __init__(self) -> None:
        # Keyed by dynamic string lineage_id -> lineage record dictionary
        self._lineage_records: dict[str, dict[str, Any]] = {}

    def record_lineage(
        self,
        prompt_name: str,
        prompt_version: str,
        rendered_prompt: str,
        input_variables: dict[str, Any],
        provider: str,
        model: str,
        response_metadata: dict[str, Any],
    ) -> str:
        """Saves a lineage snapshot linking prompt, renderer, parameters, and metadata.

        Returns a unique lineage ID (str).
        """
        lineage_id = str(uuid.uuid4())
        record = {
            "lineage_id": lineage_id,
            "timestamp": datetime.now().isoformat(),
            "prompt_name": prompt_name,
            "prompt_version": prompt_version,
            "rendered_prompt": rendered_prompt,
            "input_variables": input_variables,
            "provider": provider,
            "model": model,
            "response_metadata": response_metadata,
        }
        self._lineage_records[lineage_id] = record
        return lineage_id

    def get_lineage(self, lineage_id: str) -> dict[str, Any] | None:
        return self._lineage_records.get(lineage_id)

    def get_prompt_lineages(self, prompt_name: str) -> list[dict[str, Any]]:
        target = prompt_name.lower()
        return [
            rec
            for rec in self._lineage_records.values()
            if rec["prompt_name"].lower() == target
        ]

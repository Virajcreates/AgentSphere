import pytest

from agentsphere.ai.telemetry.lineage import PromptLineageTracker


@pytest.fixture
def tracker() -> PromptLineageTracker:
    return PromptLineageTracker()


def test_record_and_get_lineage(tracker: PromptLineageTracker) -> None:
    prompt_name = "recommendation_agent"
    prompt_version = "v2"
    rendered_prompt = "Hello Viraj, we recommend running shoes based on your budget of $120."
    input_variables = {"name": "Viraj", "budget": 120}

    lineage_id = tracker.record_lineage(
        prompt_name=prompt_name,
        prompt_version=prompt_version,
        rendered_prompt=rendered_prompt,
        input_variables=input_variables,
        provider="openai",
        model="gpt-4o",
        response_metadata={"latency": 0.8, "cost": 0.005, "tokens": 15},
    )

    # Verify we got a string ID
    assert isinstance(lineage_id, str)
    assert len(lineage_id) > 0

    # Retrieve individual lineage record
    record = tracker.get_lineage(lineage_id)
    assert record is not None
    assert record["prompt_name"] == prompt_name
    assert record["prompt_version"] == prompt_version
    assert record["rendered_prompt"] == rendered_prompt
    assert record["input_variables"]["name"] == "Viraj"
    assert record["provider"] == "openai"
    assert record["model"] == "gpt-4o"
    assert record["response_metadata"]["latency"] == 0.8

    # Query prompt lineages list
    lineages = tracker.get_prompt_lineages(prompt_name)
    assert len(lineages) == 1
    assert lineages[0]["lineage_id"] == lineage_id

    # Non-existent query returns empty
    assert tracker.get_prompt_lineages("nonexistent") == []

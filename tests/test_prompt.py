from incident_intelligence.prompt import build_incident_prompt


REMOVED_EXAMPLE_FACTS = (
    "output shaft seal",
    "oil was visible",
    "pressure dropped after startup",
)


def test_production_prompt_does_not_contain_concrete_few_shot_facts() -> None:
    prompt = build_incident_prompt(
        incident_id="INC-TEST",
        report="The controller displayed an intermittent warning during inspection.",
    ).casefold()

    for fact in REMOVED_EXAMPLE_FACTS:
        assert fact not in prompt


def test_prompt_distinguishes_guidance_from_case_evidence() -> None:
    prompt = build_incident_prompt(
        incident_id="INC-TEST",
        report="The transmitter reading became unavailable during operation.",
        knowledge_context="Signal loss can result from several diagnostic conditions.",
    )

    assert "not evidence about this case" in prompt
    assert "current incident report as the only source of case evidence" in prompt
    assert 'probable_cause to "unknown"' in prompt
    assert "Never invent unsupported evidence" in prompt

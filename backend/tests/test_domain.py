from app.domain import generate, validate, discover, verdict

def test_one_hundred_seeded_scenarios_are_valid_and_repeatable():
    variants = set()
    for seed in range(100):
        first, second = generate(seed), generate(seed)
        validate(first)
        assert (first.culprit, first.motive, first.method) == (second.culprit, second.motive, second.method)
        variants.add((first.culprit, first.motive, first.method))
    assert len(variants) >= 20

def test_undiscovered_evidence_cannot_support_verdict():
    case = generate(42)
    answer = verdict(case, {"culprit": case.culprit, "motive": case.motive, "evidence_ids": ["access_log"]})
    assert answer["score"] == 70

def test_evidence_is_location_locked():
    case = generate(42)
    try: discover(case, "access_log")
    except ValueError: pass
    else: assert False

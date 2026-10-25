import pytest

from uwazi.audit import AuditLog


@pytest.fixture
def log(tmp_path):
    return AuditLog(str(tmp_path / "a.db"))


def test_empty_chain_verifies(log):
    assert log.verify()


def test_chain_verifies_after_reviews(log):
    for i in range(3):
        log.record_review(f"A{i}", "tester", "needs_info", "code", "note")
    assert log.verify() and len(log.entries()) == 3


def test_tampering_is_detected(log):
    log.record_review("A1", "tester", "referred", "", "note")
    log.record_review("A2", "tester", "no_action", "", "")
    assert log.tamper_for_demo() and not log.verify()


def test_latest_review_wins_and_unknown_outcome_rejected(log):
    log.record_review("A1", "t", "needs_info")
    log.record_review("A1", "t", "explained_legit", "special_spec")
    assert log.latest_reviews()["A1"]["outcome"] == "explained_legit"
    with pytest.raises(ValueError):
        log.record_review("A1", "t", "guilty")


def test_notes_are_bound_to_chain_but_not_exposed(log):
    log.record_review("A1", "t", "needs_info", "", "private reviewer note")
    assert "private reviewer note" not in log.entries()[0]["detail"]

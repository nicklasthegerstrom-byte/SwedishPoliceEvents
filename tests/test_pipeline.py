
from polisprojekt.services.database import EventDB
from polisprojekt.services.notify import notify_slack
from polisprojekt.model.event_model import Event
import pytest

@pytest.fixture
def sample_event():
    return Event(
        event_id=1,
        datetime_str=None,
        type="Rån",
        summary="Test",
        name=None,
        location={},
        url=None,
        raw={},
    )

def test_mark_notified_changes_state(tmp_path):
    db = EventDB(str(tmp_path / "test.db"))

    event_id = 123

    assert db.is_notified(event_id) is False

    db.mark_notified(event_id)

    assert db.is_notified(event_id) is True


def test_notify_slack_does_not_mark_notified_when_send_fails(tmp_path, monkeypatch, sample_event):
   
    db = EventDB(str(tmp_path / "test.db"))

    e = sample_event
    
    monkeypatch.setattr(Event, "seriousness", property(lambda self: 10))
    monkeypatch.setattr(
        "polisprojekt.services.notify.send_to_slack",
        lambda *args, **kwargs: False
        )
    
    sent = notify_slack(db=db, events=[e], webhook_url="dummy", min_score=7)

    assert sent == 0
    assert db.is_notified(123) is False

def test_notify_slack_marks_event_when_send_succeeds(tmp_path, monkeypatch, sample_event):
    db = EventDB(str(tmp_path / "test.db"))

    e = sample_event

    # Tvinga seriousness att passera filtret
    monkeypatch.setattr(Event, "seriousness", property(lambda self: 10))

    # Fejka Slack-sändning → alltid True
    monkeypatch.setattr(
        "polisprojekt.services.notify.send_to_slack",
        lambda *a, **k: True
    )

    sent = notify_slack(db=db, events=[e], webhook_url="dummy", min_score=7)

    assert sent == 1
    assert db.is_notified(1) is True

def test_notify_slack_ignores_low_score(tmp_path, monkeypatch, sample_event):
    db = EventDB(str(tmp_path / "test.db"))

    e = sample_event

    # Tvinga seriousness under gränsen
    monkeypatch.setattr(Event, "seriousness", property(lambda self: 3))

    # Slack ska ALDRIG anropas här. Om den anropas vill vi att testet exploderar.
    def boom(*args, **kwargs):
        raise AssertionError("send_to_slack ska inte köras för låg score")

    monkeypatch.setattr("polisprojekt.services.notify.send_to_slack", boom)

    sent = notify_slack(db=db, events=[e], webhook_url="dummy", min_score=7)

    assert sent == 0
    assert db.is_notified(1) is False


def test_notify_slack_skips_already_notified(tmp_path, monkeypatch, sample_event):
    db = EventDB(str(tmp_path / "test.db"))

    e = sample_event

    # Gör den "serious" så den annars hade skickats
    monkeypatch.setattr(Event, "seriousness", property(lambda self: 10))

    # För-markera som notifierad
    db.mark_notified(1)
    assert db.is_notified(1) is True

    # Om Slack skulle anropas vill vi att testet dör direkt
    def boom(*args, **kwargs):
        raise AssertionError("send_to_slack ska inte köras när event redan är notifierat")

    monkeypatch.setattr("polisprojekt.services.notify.send_to_slack", boom)

    sent = notify_slack(db=db, events=[e], webhook_url="dummy", min_score=7)

    assert sent == 0
    assert db.is_notified(1) is True
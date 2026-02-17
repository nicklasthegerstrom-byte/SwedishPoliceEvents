from polisprojekt.services.database import EventDB
from polisprojekt.services.notify import send_to_discord
from polisprojekt.model.event_model import Event

def test_mark_notified_changes_state(tmp_path):
    db = EventDB(str(tmp_path / "test.db"))

    event_id = 123

    assert db.is_notified(event_id) is False

    db.mark_notified(event_id)

    assert db.is_notified(event_id) is True

from flask import Flask, render_template, request, jsonify
from datetime import datetime
from main import (
    load_events,
    get_serious_events,
    search_events_by_word,
    search_events_by_location,
)
from notify_flask import get_new_serious_events
from data.scoring import user_seriousness

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    selected_hours = "all"
    min_seriousness = 7
    keyword = ""
    location = ""

    if request.method == "POST":
        selected_hours = request.form.get("hours", "all")
        min_seriousness = int(request.form.get("min_seriousness", 7))
        keyword = request.form.get("keyword", "").strip()
        location = request.form.get("location", "").strip()

    # hämta och filtrera händelser
    events = load_events()
    hours_param = None if selected_hours == "all" else int(selected_hours)
    filtered = get_serious_events(hours=hours_param, min_score=min_seriousness)

    if keyword:
        filtered = [
        e for e in filtered
        if keyword.lower() in e.summary.lower() or keyword.lower() in e.type.lower()
        ]


    if location:
        loc_matches = search_events_by_location(location, min_score=min_seriousness)
        loc_ids = {e.id for e in loc_matches}
        filtered = [e for e in filtered if e.id in loc_ids]

    filtered = sorted(filtered, key=lambda e: e.time or datetime.min, reverse=True)

    return render_template(
        "index.html",
        events=filtered,
        selected_hours=selected_hours,
        min_seriousness=min_seriousness,
        keyword=keyword,
        location=location,
        count=len(filtered),
    )


@app.route("/check_new_events")
def check_new_events():
    """Returnerar nya allvarliga händelser för notifieringar."""
    new_events = get_new_serious_events()
    data = [
        {
            "id": e.id,
            "type": e.type,
            "location": e.location_name,
            "summary": e.summary,
            "seriousness": e.effective_seriousness,
            "url": e.url
        }
        for e in new_events
    ]
    return jsonify(data)


@app.route("/manage", methods=["GET", "POST"])
def manage():
    """Hantera användarjusterade allvarlighetsgrader."""
    if request.method == "POST":
        for key in list(user_seriousness.keys()):
            field_name = f"seriousness_{key}"
            if field_name in request.form:
                try:
                    new_val = int(request.form[field_name])
                    user_seriousness[key] = max(0, min(10, new_val))
                except ValueError:
                    continue
    return render_template("manage.html", seriousness=user_seriousness)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

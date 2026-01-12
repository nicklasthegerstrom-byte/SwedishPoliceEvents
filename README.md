# Polisens Händelsebevakning

Ett Python-projekt som hämtar och filtrerar händelser från **Polisens öppna API**.  
Användaren kan välja tidsintervall, söka efter nyckelord (t.ex. "mord", "skottlossning"), sortera händelser per ort samt öppna länkar till polisens webbplats.  

## 🚀 Funktioner
- Hämta senaste händelser (max 500) från polisens API.
- Filtrera efter tidsperiod (3h, 6h, 12h, 24h eller alla).
- Sökfunktion för att hitta specifika händelser i listan.
- Sortera händelser per ort.
- Visa klickbara länkar direkt till polisens webbplats.
- Planerade funktioner:
  - Larmfunktion (t.ex. SMS eller notiser).
  - GUI med dropdown-menyer och klickbara länkar.

## 📦 Installation

1. Klona projektet:
   ```bash
   git clone https://github.com/nicklasthegerstrom-byte/polisprojekt.git
   cd polisprojekt


   
polisprojekt/
│
├── webapp.py                # Flask-huvudfilen – startar servern, hanterar routes (/, /manage, /check_new_events)
│
├── notify_flask.py          # Håller koll på nya händelser, "seen_event_ids", filtrerar allvarliga händelser
│
├── main.py                  # Hjälpfunktioner: load_events(), get_serious_events(), search_events_by_word(), osv.
│
├── templates/               # Flask HTML-mallar
│   ├── index.html           # Huvudsidan med filter, sökfält, notisknapp och händelselista
│   └── manage.html          # Sida för att ändra allvarlighetsgrader (seriousness)
│
├── static/                  # Statisk data som CSS, JS, bilder
│   ├── style.css            # (Frivilligt) utbruten CSS om du inte vill ha den inline
│   └── script.js            # (Frivilligt) JavaScript för notiser, auto-refresh, m.m.
│
├── data/                    # (Valfritt) Lagring av hämtade händelser, cache, JSON, eller framtida databas
│   └── events.json
│
├── requirements.txt         # Lista på Python-paket (Flask m.fl.)
│
└── README.md                # Kort beskrivning, instruktioner, ev. TODO-lista

Nicks Polishändelser 1.0

Ett webbverktyg för att övervaka svenska polishändelser i realtid, filtrera dem efter allvarlighetsgrad, plats, tid och sökord – och få notiser när nya allvarliga händelser inträffar.

Byggd i Python med Flask, för redaktionell användning och snabba nyhetsbeslut.

⸻

VAD GÖR APPEN

Applikationen hämtar data från Polismyndighetens öppna API och låter dig:
	•	Se alla aktuella polishändelser
	•	Filtrera på:
	•	Tid (3h, 6h, 12h, 24h eller alla)
	•	Allvarlighetsgrad (1–10)
	•	Sökord (t.ex. mord, explosion)
	•	Plats (stad, ort, område)
	•	Justera hur allvarliga olika händelsetyper anses vara
	•	Få notiser när nya allvarliga händelser dyker upp

Det är i praktiken ett litet redaktionellt övervakningssystem för blåljusflödet.

⸻

PROJEKTSTRUKTUR

polisprojekt
webapp.py – Flask-servern (huvudapp)
main.py – Affärslogik: laddning, filtrering, sökning
notify_flask.py – Håller koll på nya allvarliga händelser

data
scoring.py – Grundallvarlighet + användarjusteringar

templates
index.html – Webbgränssnittet
manage.html – Sida för att ändra allvarlighetsgrader

static
style.css – Färger, layout, UI
script.js – Notiser och frontendlogik

requirements.txt
README.md

⸻

STARTA APPEN LOKALT
	1.	Skapa virtuell miljö (valfritt men rekommenderat)

python -m venv venv
source venv/bin/activate
	2.	Installera beroenden

pip install -r requirements.txt
	3.	Starta servern

python webapp.py
	4.	Öppna i webbläsare

http://127.0.0.1:5000

⸻

ALLVARLIGHETSGRAD

Varje händelsetyp har ett allvarlighetsvärde mellan 1 och 10.

Exempel:
Mord: 10
Explosion: 9
Rån: 7
Brand: 6
Ofredande: 3

Du kan ändra dessa i webbgränssnittet under sidan
/manage

Detta påverkar alla filter och notiser.

⸻

NOTISER

Appen kan upptäcka när nya allvarliga händelser tillkommer.

Systemet:
	•	Minns vilka event som redan setts
	•	När nya dyker upp med seriousness över vald gräns skickas notis till webbläsaren

Detta sker via en endpoint som frontend frågar regelbundet.

⸻

FÖR PRODUKTION

Detta är en Flask-utvecklingsserver.

För att köra publikt:
	•	Kör via Render, Fly.io eller Railway
	•	Använd Gunicorn eller annan WSGI-server

⸻

VARFÖR DETTA FINNS

Det är ett redaktionellt verktyg för att:
	•	Snabbt se vad polisen arbetar med i Sverige
	•	Prioritera händelser
	•	Sortera bort mindre intressanta händelser

Byggt för människor (Främst mig själv) som måste fatta nyhetsbeslut på minuter.

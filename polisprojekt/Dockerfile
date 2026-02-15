# Starta från en lättviktig Python-bild
FROM python:3.12-slim

# Ange arbetskatalog i containern
WORKDIR /app

# Installera alla dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiera in all kod
COPY . .

# Starta Flask-servern via Gunicorn (port från env)
CMD exec gunicorn --bind :$PORT webapp:app

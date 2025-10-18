# 🤝 Strand Relations AI Matchmaker

## 📋 Installation

### Förutsättningar
- Python 3.7 eller senare
- pip (Python package installer)

### Installera paket

**1. Skapa och aktivera virtuell miljö:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**2. Installera paket:**
```bash
pip install pandas numpy openpyxl
```

Eller installera från requirements.txt:
```bash
pip install -r requirements.txt
```

## 🚀 Kör programmet

### Version 1: Med Excel-fil (Lokal)
```bash
# Aktivera virtuell miljö
source .venv/bin/activate

# Kör scriptet med Excel-fil
python matchmaking.py

# Deaktivera virtuell miljö
deactivate
```

### Version 2: Med Google Sheets (Rekommenderat)
```bash
# Aktivera virtuell miljö
source .venv/bin/activate

# Följ setup-guiden för Google Sheets
# Se GOOGLE_SHEETS_SETUP.md för detaljerade instruktioner

# Kör scriptet med Google Sheets
python matchmaking_google_sheets.py

# Deaktivera virtuell miljö
deactivate
```

## 📊 Datahantering

- **Excel-version**: Använder lokal `ai_verktyg_byraer.xlsx` fil
- **Google Sheets-version**: Laddar data direkt från [din Google Sheet](https://docs.google.com/spreadsheets/d/1eyahA1utzpFzAFjJylmJwOx1y0s4Sa0yBwMgb5O7N-M/edit)
- **Fördelar med Google Sheets**: Automatiska uppdateringar, ingen lokal filhantering, bättre samarbete

---

## 🎯 Om programmet
🎯 Tillgängliga specialiseringar:
   • Aktivitet
   • Digital
   • Event
   • Foto/Film
   • Influencers
   • Koncept & Design
   • Media
   • PR
   • Produktion
   • Reklam
   • Utlandet

Vilka specialiseringar söker kunden?
Specialisering: Digital
Specialisering: Influencers  
Specialisering: klar

Önskad byråstorlek?
1. Liten (1-2 specialiseringar)
2. Mellan (3-4 specialiseringar)
3. Stor (5+ specialiseringar)
4. Spelar ingen roll
Välj (1-4): 2

🔍 Letar efter perfekta matchningar...

🏆 TOP 5 MATCHNINGAR
1. Cube
   🎯 Match: 90%
   📍 Specialiseringar: Influencers
   ⭐ Expertis: Hög

2. Cure
   🎯 Match: 90%
   📍 Specialiseringar: Influencers
   ⭐ Expertis: Hög
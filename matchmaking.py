import pandas as pd
import numpy as np
from typing import Dict, List
from google_sheets_service import GoogleSheetsService

class ByraMatchmaker:
    def __init__(self, spreadsheet_id, sheet_gid='1684807275'):
        """
        Initiera matchmaker med Google Sheets
        
        Args:
            spreadsheet_id: Google Sheets ID (från URL)
            sheet_gid: Google ID för specifikt ark (standard: '1684807275')
        """
        self.spreadsheet_id = spreadsheet_id
        self.sheet_gid = sheet_gid
        self.google_sheets = GoogleSheetsService()
        
        # Ladda data från Google Sheets
        self.byraer_df = self._ladda_fran_google_sheets()
        self.byra_lista = self._skapa_byra_database()
    
    def _ladda_fran_google_sheets(self):
        """Ladda data från Google Sheets"""
        try:
            # Hämta sheet-namnet från GID
            sheet_name = self._get_sheet_name_from_gid()
            
            # Ladda data från specifikt ark
            range_name = f'{sheet_name}!A1:Z100'
            df = self.google_sheets.get_sheet_data(self.spreadsheet_id, range_name)
            
            if df.empty:
                raise ValueError("Ingen data hittades i Google Sheets")
            
            print(f"✅ Laddade {len(df)} rader från Google Sheets (Ark: {sheet_name}, GID: {self.sheet_gid})")
            return df
            
        except Exception as e:
            print(f"❌ Fel vid laddning från Google Sheets: {e}")
            raise
    
    def _get_sheet_name_from_gid(self):
        """Hämta sheet-namn från GID"""
        try:
            # Hämta alla sheets från spreadsheetet
            sheet_metadata = self.google_sheets.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            sheets = sheet_metadata.get('sheets', [])
            
            # Hitta sheet med rätt GID
            for sheet in sheets:
                sheet_id = sheet['properties']['sheetId']
                if str(sheet_id) == str(self.sheet_gid):
                    return sheet['properties']['title']
            
            # Om GID inte hittas, använd första sheetet
            if sheets:
                return sheets[0]['properties']['title']
            
            raise ValueError(f"Inget ark hittades med GID: {self.sheet_gid}")
            
        except Exception as e:
            print(f"❌ Fel vid hämtning av sheet-namn: {e}")
            # Fallback till standardnamn
            return "strandsagencies"
    
    def _skapa_byra_database(self):
        """Konvertera Google Sheets-data till en lista med byråobjekt"""
        byraer = []
        
        # Gå igenom varje kolumn (specialisering)
        for kolumn in self.byraer_df.columns:
            specialisering = kolumn.strip()
            
            # Hoppa över tomma kolumner
            if not specialisering or specialisering.startswith('Unnamed'):
                continue
            
            # Gå igenom varje cell i kolumnen
            for idx, cell in enumerate(self.byraer_df[kolumn]):
                if pd.notna(cell) and str(cell).strip() != '':
                    byra_namn = str(cell).strip()
                    
                    # Kolla om byrån redan finns
                    existerande_byra = next((b for b in byraer if b['namn'] == byra_namn), None)
                    
                    if existerande_byra:
                        # Lägg till specialisering till existerande byrå
                        existerande_byra['specialiseringar'].append(specialisering)
                    else:
                        # Skapa ny byrå
                        byraer.append({
                            'namn': byra_namn,
                            'specialiseringar': [specialisering],
                            'lank': cell if 'http' in str(cell) else None
                        })
        
        return byraer
    
    def _rensa_namn(self, namn):
        """Rensa byrånamn från onödigt innehåll"""
        namn = str(namn).split(' ')[0]  # Ta första ordet
        namn = namn.replace('https://', '').replace('www.', '')
        return namn.split('.')[0]  # Ta bort domänändelse
    
    def berakna_match_score(self, byra, kund_behov):
        """Beräkna matchningsscore mellan byrå och kundbehov"""
        score = 0
        max_score = 100
        
        # Räkna antal matchande specialiseringar
        matchande_specialiseringar = set(byra['specialiseringar']) & set(kund_behov['specialiseringar'])
        antal_matchande = len(matchande_specialiseringar)
        antal_onskade = len(kund_behov['specialiseringar'])
        
        if antal_onskade == 0:
            return 0
        
        # Grundscore baserat på antal matchningar
        grundscore = (antal_matchande / antal_onskade) * 80
        
        # Bonus för byråstorlek (om specificerad)
        if 'byra_storlek' in kund_behov and kund_behov['byra_storlek'] != 'Spelar ingen roll':
            byra_antal_spec = len(byra['specialiseringar'])
            onskad_storlek = kund_behov['byra_storlek']
            
            if onskad_storlek == 'Liten (1-2 specialiseringar)' and byra_antal_spec <= 2:
                grundscore += 10
            elif onskad_storlek == 'Mellan (3-4 specialiseringar)' and 3 <= byra_antal_spec <= 4:
                grundscore += 10
            elif onskad_storlek == 'Stor (5+ specialiseringar)' and byra_antal_spec >= 5:
                grundscore += 10
        
        # Bonus för exakt matchning
        if antal_matchande == antal_onskade:
            grundscore += 10
        
        return min(grundscore, max_score)
    
    def hitta_matchningar(self, kund_behov):
        """Hitta bästa matchningar baserat på kundbehov"""
        if not kund_behov['specialiseringar']:
            return []
        
        # Beräkna score för varje byrå
        byraer_med_score = []
        for byra in self.byra_lista:
            score = self.berakna_match_score(byra, kund_behov)
            if score > 0:  # Bara inkludera byråer med matchning
                byraer_med_score.append({
                    'byra': byra,
                    'score': score
                })
        
        # Sortera efter score (högst först)
        byraer_med_score.sort(key=lambda x: x['score'], reverse=True)
        
        return byraer_med_score[:5]  # Returnera top 5
    
    def visa_tillgangliga_specialiseringar(self):
        """Visa alla tillgängliga specialiseringar"""
        alla_specialiseringar = set()
        for byra in self.byra_lista:
            alla_specialiseringar.update(byra['specialiseringar'])
        
        print("🎯 Tillgängliga specialiseringar:")
        for spec in sorted(alla_specialiseringar):
            if spec and not spec.startswith('Unnamed'):
                print(f"   • {spec}")
        print()

def skapa_kund_behov_interaktivt():
    """Interaktiv funktion för att samla in kundbehov"""
    print("🤝 Välkommen till Strand Relations AI Matchmaker!")
    print("=" * 50)
    
    # Visa tillgängliga specialiseringar
    print("🎯 Tillgängliga specialiseringar:")
    print("   • Aktivitet")
    print("   • Digital")
    print("   • Event")
    print("   • Foto/Film")
    print("   • Influencers")
    print("   • Koncept & Design")
    print("   • Media")
    print("   • PR")
    print("   • Produktion")
    print("   • Reklam")
    print("   • Utlandet")
    print()
    
    # Samla in kundbehov
    kund_behov = {}
    specialiseringar = []
    
    print("Vilka specialiseringar söker kunden? (skriv 'klar' när du är färdig)")
    while True:
        specialisering = input("Specialisering: ").strip()
        if specialisering.lower() == 'klar':
            break
        if specialisering:
            specialiseringar.append(specialisering)
    
    kund_behov['specialiseringar'] = specialiseringar
    
    # Fråga om byråstorlek
    print("\nÖnskad byråstorlek?")
    print("1. Liten (1-2 specialiseringar)")
    print("2. Mellan (3-4 specialiseringar)")
    print("3. Stor (5+ specialiseringar)")
    print("4. Spelar ingen roll")
    
    while True:
        try:
            val = input("Välj (1-4): ").strip()
            if val in ['1', '2', '3', '4']:
                storlekar = {
                    '1': 'Liten (1-2 specialiseringar)',
                    '2': 'Mellan (3-4 specialiseringar)',
                    '3': 'Stor (5+ specialiseringar)',
                    '4': 'Spelar ingen roll'
                }
                kund_behov['byra_storlek'] = storlekar[val]
                break
            else:
                print("Välj 1, 2, 3 eller 4")
        except KeyboardInterrupt:
            print("\nAvbrutet av användare")
            return None
    
    return kund_behov

def visa_matchningar(matchningar):
    """Visa matchningar på ett snyggt sätt"""
    if not matchningar:
        print("❌ Inga matchningar hittades")
        return
    
    print("\n🔍 Letar efter perfekta matchningar...")
    print()
    print("🏆 TOP 5 MATCHNINGAR")
    
    for i, match in enumerate(matchningar, 1):
        byra = match['byra']
        score = match['score']
        
        # Bestäm expertisnivå baserat på score
        if score >= 90:
            expertis = "Hög"
        elif score >= 70:
            expertis = "Medel"
        else:
            expertis = "Låg"
        
        print(f"\n{i}. {byra['namn']}")
        print(f"   🎯 Match: {score:.0f}%")
        print(f"   📍 Specialiseringar: {', '.join(byra['specialiseringar'])}")
        print(f"   ⭐ Expertis: {expertis}")
        
        if byra.get('lank'):
            print(f"   🔗 Länk: {byra['lank']}")

def main():
    """Huvudfunktion för att köra matchmakern"""
    try:
        # Google Sheets ID - från din Google Sheet URL
        SPREADSHEET_ID = "1eyahA1utzpFzAFjJylmJwOx1y0s4Sa0yBwMgb5O7N-M"
        
        # Initiera matchmaker med specifikt ark (GID: 1684807275)
        matchmaker = ByraMatchmaker(SPREADSHEET_ID, sheet_gid='1684807275')
        
        # Samla in kundbehov
        kund_behov = skapa_kund_behov_interaktivt()
        
        if not kund_behov:
            return
        
        # Hitta matchningar
        matchningar = matchmaker.hitta_matchningar(kund_behov)
        
        # Visa resultat
        visa_matchningar(matchningar)
        
    except Exception as e:
        print(f"❌ Ett fel uppstod: {e}")
        print("Kontrollera att Google Sheets är korrekt konfigurerat.")

if __name__ == "__main__":
    main()

import pandas as pd
import numpy as np
from typing import Dict, List

class ByraMatchmaker:
    def __init__(self, excel_fil):
        # Ladda och förbered data
        self.byraer_df = pd.read_excel(excel_fil, sheet_name='Byråer')
        self.byra_lista = self._skapa_byra_database()
    
    def _skapa_byra_database(self):
        """Konvertera Excel-data till en lista med byråobjekt"""
        byraer = []
        
        # Gå igenom varje kolumn (specialisering)
        for kolumn in self.byraer_df.columns:
            specialisering = kolumn.strip()
            
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
        
        # 1. SPECIALISERINGSMATCH (60 poäng)
        kund_specialiseringar = kund_behov['specialiseringar']
        byra_specialiseringar = byra['specialiseringar']
        
        for spec in kund_specialiseringar:
            if spec in byra_specialiseringar:
                score += 60 / len(kund_specialiseringar)
        
        # 2. STORLEKSMATCH (20 poäng)
        if 'storlek_preferens' in kund_behov:
            # Anta att byråer med färre specialiseringar är mindre
            antal_spec = len(byra_specialiseringar)
            if antal_spec <= 2 and kund_behov['storlek_preferens'] == 'liten':
                score += 20
            elif 3 <= antal_spec <= 4 and kund_behov['storlek_preferens'] == 'mellan':
                score += 20
            elif antal_spec >= 5 and kund_behov['storlek_preferens'] == 'stor':
                score += 20
        
        # 3. EXPERTISDJUP (20 poäng)
        # Byråer med färre specialiseringar kan vara mer specialiserade
        if len(byra_specialiseringar) <= 3:
            score += 20
        elif len(byra_specialiseringar) <= 5:
            score += 10
        
        return min(score, max_score)
    
    def hitta_match(self, kund_behov, antal_resultat=5):
        """Hitta bäst matchande byråer baserat på kundbehov"""
        resultat = []
        
        for byra in self.byra_lista:
            match_score = self.berakna_match_score(byra, kund_behov)
            
            if match_score > 0:  # Visa bara byråer med någon match
                resultat.append({
                    'namn': byra['namn'],
                    'match_score': round(match_score),
                    'specialiseringar': ', '.join(byra['specialiseringar']),
                    'lank': byra['lank'],
                    'expertis_djup': 'Hög' if len(byra['specialiseringar']) <= 3 else 'Medel'
                })
        
        # Sortera efter match score
        resultat.sort(key=lambda x: x['match_score'], reverse=True)
        return resultat[:antal_resultat]
    
    def visa_tillgangliga_specialiseringar(self):
        """Visa alla tillgängliga specialiseringar i databasen"""
        alla_specialiseringar = set()
        for byra in self.byra_lista:
            alla_specialiseringar.update(byra['specialiseringar'])
        
        print("🎯 Tillgängliga specialiseringar:")
        for spec in sorted(alla_specialiseringar):
            print(f"   • {spec}")
        print()

def skapa_kund_behov_interaktivt():
    """Interaktiv funktion för att samla in kundbehov"""
    print("🤝 Välkommen till Strand Relations AI Matchmaker!")
    print("=" * 50)
    
    # Visa tillgängliga specialiseringar
    matchmaker = ByraMatchmaker('ai_verktyg_byraer.xlsx')
    matchmaker.visa_tillgangliga_specialiseringar()
    
    # Samla in kundbehov
    kund_behov = {}
    
    # Specialiseringar
    print("Vilka specialiseringar söker kunden? (skriv 'klar' när du är färdig)")
    specialiseringar = []
    while True:
        spec = input("Specialisering: ").strip()
        if spec.lower() == 'klar':
            break
        if spec:
            specialiseringar.append(spec)
    
    kund_behov['specialiseringar'] = specialiseringar
    
    # Storlekspreferens
    print("\nÖnskad byråstorlek?")
    print("1. Liten (1-2 specialiseringar)")
    print("2. Mellan (3-4 specialiseringar)") 
    print("3. Stor (5+ specialiseringar)")
    print("4. Spelar ingen roll")
    
    val = input("Välj (1-4): ").strip()
    storlek_map = {'1': 'liten', '2': 'mellan', '3': 'stor'}
    kund_behov['storlek_preferens'] = storlek_map.get(val, 'bryr mig inte')
    
    return kund_behov

def main():
    """Huvudfunktion för att köra matchmakern"""
    try:
        # Initiera matchmaker
        matchmaker = ByraMatchmaker('ai_verktyg_byraer.xlsx')
        
        # Samla in kundbehov
        kund_behov = skapa_kund_behov_interaktivt()
        
        # Hitta matchningar
        print("\n🔍 Letar efter perfekta matchningar...")
        resultat = matchmaker.hitta_match(kund_behov, antal_resultat=8)
        
        # Presentera resultat
        print(f"\n🏆 TOP {len(resultat)} MATCHNINGAR")
        print("=" * 60)
        
        for i, byra in enumerate(resultat, 1):
            print(f"{i}. {byra['namn']}")
            print(f"   🎯 Match: {byra['match_score']}%")
            print(f"   📍 Specialiseringar: {byra['specialiseringar']}")
            print(f"   ⭐ Expertis: {byra['expertis_djup']}")
            if byra['lank']:
                print(f"   🔗 Länk: {byra['lank']}")
            print()
            
    except Exception as e:
        print(f"❌ Ett fel uppstod: {e}")
        print("Kontrollera att Excel-filen finns och har rätt format.")

if __name__ == "__main__":
    main()
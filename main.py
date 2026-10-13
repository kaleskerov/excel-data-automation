import glob
import sys

import pandas as pd

KOLUMNY_GLOWNE = ['ID', 'Imie_Nazwisko', 'Stawka_godzinowa']
KOLUMNY_SZCZEGOLY = ['ID', 'Data', 'Godziny']
MAX_GODZIN_DZIENNIE = 24


def wczytaj_glowne(sciezka='dane_glowne.xlsx'):
    """Wczytuje plik bazowy i sprawdza kolumny oraz unikalnosc ID."""
    df = pd.read_excel(sciezka)
    brakujace = [c for c in KOLUMNY_GLOWNE if c not in df.columns]
    if brakujace:
        raise ValueError(f"Brak kolumn w pliku bazowym: {brakujace}")
    if df['ID'].duplicated().any():
        raise ValueError("Duplikaty ID w pliku bazowym!")
    df['Stawka_godzinowa'] = pd.to_numeric(df['Stawka_godzinowa'], errors='coerce')
    return df.dropna(subset=['Stawka_godzinowa'])


def waliduj_szczegoly(df, nazwa='dane'):
    """Usuwa bledne wiersze (puste/ujemne/zbyt duze godziny, brak daty)
    i zwraca (poprawne_dane, lista_ostrzezen)."""
    ostrzezenia = []
    df = df.copy()
    df['Godziny'] = pd.to_numeric(df['Godziny'], errors='coerce')
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')

    bledne = (
        df['Godziny'].isna()
        | (df['Godziny'] <= 0)
        | (df['Godziny'] > MAX_GODZIN_DZIENNIE)
        | df['Data'].isna()
        | df['ID'].isna()
    )
    if bledne.any():
        ostrzezenia.append(f"{nazwa}: pominieto {int(bledne.sum())} blednych wierszy")
    df = df[~bledne]

    duplikaty = df.duplicated(subset=['ID', 'Data'], keep='first')
    if duplikaty.any():
        ostrzezenia.append(f"{nazwa}: usunieto {int(duplikaty.sum())} duplikatow (ID + Data)")
    return df[~duplikaty], ostrzezenia


def wczytaj_szczegoly(wzorzec='czesc_danych_*.xlsx'):
    """Wczytuje wszystkie pliki pasujace do wzorca i laczy je w jedna tabele."""
    ramki, ostrzezenia = [], []
    for plik in sorted(glob.glob(wzorzec)):
        df = pd.read_excel(plik)
        if not all(c in df.columns for c in KOLUMNY_SZCZEGOLY):
            ostrzezenia.append(f"{plik}: brak wymaganych kolumn, plik pominiety")
            continue
        df, ost = waliduj_szczegoly(df, plik)
        ostrzezenia.extend(ost)
        ramki.append(df)
    if not ramki:
        return pd.DataFrame(columns=KOLUMNY_SZCZEGOLY), ostrzezenia
    wszystkie = pd.concat(ramki, ignore_index=True)
    # ten sam dzien w roznych plikach tez liczymy tylko raz
    duplikaty = wszystkie.duplicated(subset=['ID', 'Data'], keep='first')
    if duplikaty.any():
        ostrzezenia.append(f"Usunieto {int(duplikaty.sum())} duplikatow miedzy plikami")
    return wszystkie[~duplikaty].reset_index(drop=True), ostrzezenia


def policz(df_szczegoly, df_glowne):
    """Laczy dane, liczy wynagrodzenie. Zwraca (dane, podsumowanie, ostrzezenia)."""
    ostrzezenia = []
    nieznane = set(df_szczegoly['ID']) - set(df_glowne['ID'])
    if nieznane:
        ostrzezenia.append(f"ID bez danych w pliku bazowym (pominiete): {sorted(nieznane)}")

    df = pd.merge(df_szczegoly, df_glowne, on='ID', how='inner')
    df['Wynagrodzenie'] = df['Godziny'] * df['Stawka_godzinowa']
    podsumowanie = (
        df.groupby(['ID', 'Imie_Nazwisko'])
        .agg(Godziny=('Godziny', 'sum'), Wynagrodzenie=('Wynagrodzenie', 'sum'))
        .reset_index()
    )
    return df, podsumowanie, ostrzezenia


def main():
    try:
        glowne = wczytaj_glowne()
    except FileNotFoundError:
        print("Blad: Nie znaleziono pliku dane_glowne.xlsx!")
        return 1
    except ValueError as e:
        print(f"Blad: {e}")
        return 1

    szczegoly, ostrzezenia = wczytaj_szczegoly()
    if szczegoly.empty:
        print("Brak poprawnych danych szczegolowych do analizy.")
        return 1

    df, podsumowanie, ost = policz(szczegoly, glowne)
    for o in ostrzezenia + ost:
        print("Ostrzezenie:", o)

    with pd.ExcelWriter('raport_koncowy.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Dane_Szczegolowe', index=False)
        podsumowanie.to_excel(writer, sheet_name='Podsumowanie', index=False)
    print("Sukces! Raport zostal zapisany jako raport_koncowy.xlsx")
    return 0


if __name__ == '__main__':
    sys.exit(main())

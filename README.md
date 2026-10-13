# Automatyzacja obsługi plików Excel z wykorzystaniem języka Python

## Opis projektu
Projekt ma na celu automatyzację procesu rozliczania czasu pracy i wynagrodzeń kierowców. Skrypt w języku Python pobiera dane z pliku bazowego (zawierającego dane pracowników i ich stawki) oraz z wielu plików szczegółowych (zawierających raporty godzinowe z poszczególnych dni). 
Następnie dane są walidowane, łączone i agregowane, a wynik zapisywany jest do nowego pliku Excel z wieloma arkuszami.

## Struktura plików i kolumn
1. **dane_glowne.xlsx** (plik bazowy):
   - `ID` - unikalny identyfikator pracownika
   - `Imie_Nazwisko` - imię i nazwisko pracownika
   - `Stawka_godzinowa` - stawka za jedną godzinę pracy

2. **czesc_danych_01.xlsx** / **czesc_danych_02.xlsx** (pliki z danymi szczegółowymi):
   - `ID` - identyfikator pracownika (klucz do łączenia)
   - `Data` - data wykonania pracy
   - `Godziny` - liczba przepracowanych godzin danego dnia

## Wymagania i instalacja
Aby uruchomić projekt, upewnij się, że masz zainstalowanego Pythona. Następnie zainstaluj wymagane biblioteki za pomocą menedżera pakietów `pip`:

```bash
pip install pandas openpyxl pytest
```

## Uruchomienie i testy
```bash
python main.py   # generuje raport_koncowy.xlsx
pytest           # uruchamia testy (walidacja danych, obliczenia)
```

## Walidacja danych
- wszystkie pliki `czesc_danych_*.xlsx` w folderze sa wczytywane automatycznie
- odrzucane sa wiersze z pusta data, pustymi, ujemnymi lub zbyt duzymi (>24 h) godzinami
- duplikaty (to samo ID i ta sama data) sa liczone tylko raz
- ID, ktorych nie ma w pliku bazowym, sa pomijane z ostrzezeniem

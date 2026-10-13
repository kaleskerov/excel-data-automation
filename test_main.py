import pandas as pd
import pytest

from main import policz, waliduj_szczegoly

GLOWNE = pd.DataFrame({'ID': [1, 2], 'Imie_Nazwisko': ['Jan Kowalski', 'Piotr Nowak'],
                       'Stawka_godzinowa': [40, 50]})


def szczegoly(rows):
    return pd.DataFrame(rows, columns=['ID', 'Data', 'Godziny'])


def test_wynagrodzenie_to_godziny_razy_stawka():
    s = szczegoly([(1, '2026-09-01', 8), (1, '2026-09-02', 10)])
    _, podsumowanie, _ = policz(waliduj_szczegoly(s)[0], GLOWNE)
    assert podsumowanie.loc[0, 'Godziny'] == 18
    assert podsumowanie.loc[0, 'Wynagrodzenie'] == 18 * 40


def test_nieznane_id_jest_pomijane_z_ostrzezeniem():
    s = szczegoly([(1, '2026-09-01', 8), (99, '2026-09-01', 5)])
    df, _, ostrzezenia = policz(waliduj_szczegoly(s)[0], GLOWNE)
    assert 99 not in df['ID'].values
    assert any('99' in o for o in ostrzezenia)


@pytest.mark.parametrize('godziny', [-3, 0, 25, 'abc', None])
def test_bledne_godziny_sa_odrzucane(godziny):
    s = szczegoly([(1, '2026-09-01', godziny), (2, '2026-09-01', 6)])
    poprawne, ostrzezenia = waliduj_szczegoly(s)
    assert list(poprawne['ID']) == [2]
    assert ostrzezenia


def test_brak_daty_jest_odrzucany():
    s = szczegoly([(1, None, 8)])
    poprawne, _ = waliduj_szczegoly(s)
    assert poprawne.empty


def test_duplikat_id_i_daty_liczony_raz():
    s = szczegoly([(1, '2026-09-01', 8), (1, '2026-09-01', 8)])
    poprawne, ostrzezenia = waliduj_szczegoly(s)
    assert len(poprawne) == 1
    assert ostrzezenia

# Heap

## Opis działania programu
Program Heap służy do analizy przestrzeni dyskowej. Jego głównym celem jest pomoc użytkownikowi w szybkim i wygodnym przeszukiwaniu wybranych katalogów, aby znaleźć duplikaty plików lub wykonać ogólną analizę zajętego miejsca. Wszystkie wyniki wyświetlane są w uporządkowany sposób w interfejsie graficznym (GUI)

Główne funkcjonalności:
- Szukanie duplikatów plików w wybranym folderze lub na wybranym dysku.
- Analiza zawartości katalogu/dysku i wyświetlanie wyników w uporządkowany sposób
- Możliwość usuwania wybranych plików i katalogów z poziomu programu.
- Wygodna nawigacja i przeglądanie katalogów (możliwość wejścia w wybrany folder poprzez dwukrotne kliknięcie).

## Instrukcja uruchomienia

Program wykorzystuje wbudowaną bibliotekę `tkinter` oraz biblioteki zewnętrzne: `psutil` (do pobierania informacji o dyskach) i `customtkinter` (dla poszczególnych komponentów GUI).

Aby uruchomić projekt, należy:

1. Pobrać wymagane biblioteki wpisując komendę:
    `pip install -r requirements.txt`
    lub
   `pip install psutil customtkinter`

2. W terminalu przejdź do katalogu źródłowego projektu:
   `cd src`

3. Uruchom program komendą:
   `python3 main.py`
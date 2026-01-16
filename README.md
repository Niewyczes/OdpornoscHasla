1. WPROWADZENIE
Password Strength Analyzer to aplikacja desktopowa napisana w języku Python
z wykorzystaniem biblioteki Tkinter. Program służy do analizy siły haseł
oraz symulacji popularnych metod ich łamania w celach edukacyjnych.

Aplikacja NIE służy do rzeczywistych ataków. Wszystkie testy mają charakter
symulacyjny i edukacyjny.


2. CEL PROJEKTU
- pokazanie jak łatwe do złamania są słabe hasła
- nauka bezpiecznego tworzenia haseł
- demonstracja ataków typu brute-force, słownikowych i maskowych
- nauka testów jednostkowych w Pythonie
- rozdzielenie logiki od interfejsu graficznego


3. FUNKCJONALNOSCI APLIKACJI
1) Analiza siły hasła
- ocena w skali 0–100
- klasyfikacja: bardzo słabe, słabe, średnie, silne, bardzo silne
- analiza długości hasła
- analiza znaków (małe, duże litery, cyfry, znaki specjalne)
- wykrywanie powtórzeń znaków
- sprawdzanie haseł słownikowych

2) Test schematyczności (Human Pattern Test)
- wykrywa popularne schematy tworzone przez ludzi
- imię + cyfry
- imię + rok
- powtórzenia słów
- proste modyfikacje haseł
- limit czasu: 10 sekund

3) Atak maskowy (Mask Attack)
- automatyczne tworzenie maski hasła
- symbole maski:
  ?l – małe litery
  ?u – duże litery
  ?d – cyfry
  ?s – znaki specjalne
- obliczanie liczby kombinacji
- raport końcowy

4) Test słownikowy
- sprawdzanie hasła w słowniku popularnych haseł
- generowanie prostych wariacji (np. haslo123)
- raport z ostrzeżeniem

5) Brute-force (symulacja)
- edukacyjna symulacja ataku
- ograniczona liczba prób
- wizualizacja postępu

4. OPIS PLIKOW

index.py
- zawiera interfejs graficzny (Tkinter)
- obsługuje przyciski i raporty
- integruje wszystkie testy
- NIE jest testowany jednostkowo

strength_logic.py
- zawiera czystą logikę analizy hasła
- brak zależności od GUI
- przeznaczony do testów jednostkowych

human_pattern_test.py
- wykrywa schematyczne hasła
- generuje losowe wzorce
- tworzy raport końcowy

mask_test.py
- tworzy maskę hasła
- symuluje mask attack
- liczy kombinacje

5. TESTY JEDNOSTKOWE
Projekt wykorzystuje bibliotekę pytest.

Testy sprawdzają:
- poprawność obliczeń
- stabilność algorytmów
- działanie logiki bez GUI

Dlaczego nie testujemy GUI?
- GUI jest trudne do testowania automatycznego
- testujemy tylko logikę
- dobra praktyka programistyczna

Przykład testu:

test_strength.py:
- test słabego hasła
- test silnego hasła
- test pustego hasła


6. URUCHAMIANIE PROJEKTU
Uruchomienie aplikacji:
python index.py

Uruchomienie testów:
pytest -v


7. WYMAGANIA
- Python 3.10 lub nowszy
- pytest (do testów)
- system Windows / Linux / macOS


8. OGRANICZENIA
- brak prawdziwego łamania haseł
- testy mają charakter edukacyjny
- brak testów GUI
- ograniczenia czasowe testów


9. PODSUMOWANIE
Projekt Password Strength Analyzer:
- uczy bezpieczeństwa haseł
- pokazuje podstawy testów jednostkowych
- stosuje poprawną architekturę (logika ≠ GUI)
- nadaje się jako projekt szkolny lub do portfolio

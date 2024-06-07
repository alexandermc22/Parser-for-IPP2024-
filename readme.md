Implementační dokumentace k 1. úloze do IPP 2023/2024
Jméno a příjmení: Alexandr Tihanschi
Login: xtihan00

## Úvod
Při vytváření parseru pro IPPcode24 jsem měl nejprve na výběr ze dvou možností. 
1) Vytvořit více tříd pro název instrukce, její argumenty a jejich typy. A pak postupně získávat 1 token a přecházet do různých stavů (konečný automat)
2) Vytvořit 1 třídu, kde každá její instance bude uchovávat několik tokenů najednou a dohromady budou představovat jednu celou instrukci.

Zvolil jsem druhou možnost, protože ji považuji za výhodnější než první, např.
- Pokud bude nutné přidat instrukci do IPPcode24, bude stačit přidat jeden řádek ve funkci definice povolených příkazů.
- Poměrně jednoduchá struktura kódu: 
    Získat řetězec -> Zkontrolovat správnost -> Převést na XML kód


Z mínusů mohu vyzdvihnout, že při implementaci první varianty bych ve větší míře využil OOP,ale při řešení jsem se snažil využít základní prvky OOP (metody, konstruktor, porovnání tříd atd.).

## Konstrukce kódu

Skript lze rozdělit do 6 hlavních částí
1) Deklarace a definice 
    > Tato část kódu deklaruje třídu, její metody a funkci pro definici existujících příkazů v IPPcode24.
2) Konverze řetězců 
    > Při čtení řetězce ze vstupu je třeba jej nejprve zpracovat, zkontrolovat první výskyt a obsah hlavičky.
    > Jako první přeskočit všechny prázdné řádky nebo řádky s komentáři
    > Za druhé odstranit všechny nepotřebné bílé znaky.
    > Za třetí, oddělte instrukci od komentáře. 
3) Vytvoření tokenu
    > Poté ze zpracovaného řetězce získáme jednotlivé tokeny
    > a v závislosti na typu provedeme syntaktickou a lexikální kontrolu (pomocí funkcí z bloku 4),
    > načež naplníme instanci třídy  
4) Pomocné funkce 
    > Implementace funkcí pro kontrolu správnosti zápisu hodnot proměnných
5) Generování kódu XML
    > funkce vygeneruje z přijatých instrukcí kód XML a vypíše jej na standardní výstup.
6) Main
    > Hlavní funkce Main, kde se kontrolují parametry skriptu, definuje se pole pro ukládání instrukcí pro čtení a volají se hlavní funkce z bloku 1 až 5.
    > Důležité je také zmínit, že mezi bloky 3 a 5 funkce main se volá metoda třídy, která kontroluje,
    > zda přijatá instrukce odpovídá deklarovaným instrukcím IPPcode24 podle názvu a typu parametru.


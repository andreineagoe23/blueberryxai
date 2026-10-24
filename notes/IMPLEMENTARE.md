# Jurnal de implementare: secțiunea E

Document de lucru, actualizat pe parcurs. Planul aprobat:
`~/.claude/plans/poti-face-un-plan-synchronous-cocoa.md`. Capcanele: `notes/AUDIT_CAPCANE.md`.

## Cum se rulează

O singură dată, din rădăcina proiectului:

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Apoi, de fiecare dată:

```
cd date
../.venv/bin/python ../src/main.py
```

Cu venv-ul activat (`source ../.venv/bin/activate`), comanda devine `python ../src/main.py`.
Pe macOS nu există `python` fără venv, doar `python3`, iar Python-ul din Homebrew nu permite
`pip install` global (PEP 668). De aici nevoia de venv.

Testele: `.venv/bin/python -m pytest tests` (din rădăcină).

`.venv/` nu intră în zip-ul final.

## Situația actuală (24.10.2026)

| Element | Stare |
|---|---|
| Config: `run.toml`, `catalogue.toml`, `template_E.toml`, `decisions.toml` | gata |
| Cod: `src/main.py`, `src/sfcr/` (workbook, locate, money, checks, decisions, evidence, compose, pipeline, backtest, outputs) | gata |
| `output/`: 7 fișiere, generate de program | gata; două rulări dau fișiere identice octet cu octet |
| Teste: 47 (34 pe copii stricate ale registrului 2025, 8 pe decizii și dovezi, 5 pe format) | toate trec, pe Python 3.11 și 3.14 |
| Rulare pe 21 de mutații agresive (foaie ștearsă, antete inversate, formulă circulară, SCR = 0, documente lipsă) | nicio cădere; cod de eroare doar dacă lipsește `registru_2025.xlsx` |
| `README.md` nou (instalare, comanda, presupuneri) | gata; enunțul temei e în `notes/ASSESSMENT.md` |
| `ai/AI.md` + exportul conversațiilor | **de făcut** |
| Verificarea DESIGN.md față de implementare | afirmațiile corectate (back-test, 34 de registre stricate, coridorul MCR, regula nivelului 1); comprimat de la 2.348 la 2.093 cuvinte, diagrama sistemului de la 36 la 26 de rânduri: 4 pagini A4 la 11pt și interlinie 1,25, 5 pagini la interlinie 1,4; **de revizuit de Andrei** |

Rezultatul pe datele reale: fonduri proprii 293,7 (nivel 1 262,4, nivel 2 31,2, nivel 3 „nu a deținut”);
dividende 15,0; SCR 148,8, „în scădere față de 151,9 … în principal ca urmare a scăderii riscului de piață”;
rata 197,4 % (decizie din config); MCR = un singur gap, fără „acoperită integral”. Back-test-ul pe 2024
reproduce 10 sloturi din E (al 11-lea, nivelul 3, e o diferență așteptată) și găsește „12,6” mapat greșit (C7 în loc de C6) și capcana „12,4” din „412,4”.

## Ce s-a schimbat față de plan

1. **Câmpuri structurate în `decisions.toml`**, pentru ca regulile să fie verificabile de cod, nu doar descrise:
   - `scr-change-cause`: `explains = "scr"`, `direction = "down"`, `clause` (care trebuie să fie parte din citat)
     în loc de `applies_if` text liber;
   - `dividends-paid-2025`: `label = "Dividende plătite"` (citatul trebuie să fie prima sumă după etichetă,
     ca să nu fie luată coloana 2024) și `figure = "dividends"`;
   - `mcr-pending`: `explains_gap = "mcr"` (citatul intră în motivul gap-ului MCR);
   - `forbidden_terms` la cererea privind reasigurarea (textul e verificat să nu le conțină);
   - refuz explicit nou pentru cererea 2 din email („puneți cifra de anul trecut”);
   - locațiile în română („paragraful 4”), pentru că apar în textul draftului.
2. **Verificare nouă: coridorul MCR** (25–45 % din SCR). Nu era în plan; prinde un MCR introdus greșit
   când va fi completat.
3. **Valoarea SCR de anul trecut** cere cel puțin două surse care concordă, dintre: registrul 2024,
   coloana „an anterior” din 2025 și textul raportului 2024. În plan scria „din trei surse; dacă nu concordă → gap”;
   acum merge și când lipsește una dintre ele.
4. **Rata din registru lipsă sau ilizibilă** (text, celulă neformatată ca procent): se folosește calculul,
   cu o notă în probleme. Nu e conflict, pentru că există o singură valoare.
5. **Două foi vizibile care se recunosc amândouă drept „Capital”** (de exemplu copia veche, făcută vizibilă
   și cu titlul schimbat): etichetele găsite pe amândouă devin gap. În plan nu era decis cum se tratează.
6. **Foaia preferată negăsită** (redenumită și cu alt titlu): căutarea continuă în toate foile vizibile, cu o notă;
   etichetele care apar pe mai multe foi (de exemplu „SCR”) devin gap.
7. **Verificări pe textul final**, adăugate: fiecare sumă și procent din text vine dintr-o figură;
   niciun termen interzis; nicio secvență de 6 cuvinte comună cu textul Dunărea. Ultima rulează doar pe corpul
   secțiunii, nu pe titlul standard al raportului.
8. **Propoziție întreagă ca gap** (`whole_gap_on`) pentru MCR și SCR: dacă cifra lipsește, propoziția devine
   un singur `[de completat: …]`, nu trei gap-uri înșirate.
9. **Back-test-ul folosește același șablon** citit ca tipar, nu mappingul. Mappingul 2024 e doar validat.
   Același mecanism citește SCR-ul de anul trecut din raport, iar anul viitor va citi draftul 2025 (testat).
10. **Manifestul** listează toate fișierele din `date/`, cu `read_by_program`; emailul, PV-ul CA scanat
    și sinteza apar ca necitite.
11. **Modul nou `pipeline.py`** (analiza unui an), ca back-test-ul să refolosească exact același cod;
    în plan, orchestrarea era în `main.py`.

12. **(24.10) Textele din `decisions.toml` sunt în română** (reguli, motive, claim-uri, cereri refuzate),
    pentru că ajung în `probleme_E_2025.md`, citit de echipa CFO-ului. Dovezile au acum `reason`, iar textul fix
    are `source`; lista de probleme are o secțiune nouă, „Text fix aprobat”. Logica și `observed` nu s-au schimbat.
13. **(24.10) Back-test: nivelul 3 e „așteptat”, nu „diferă”.** În registrul 2024 rândul nu există, iar fraza
    din 2024 se sprijinea pe lipsa lui. O figură listată ca `optional` într-o verificare de sumă, care lipsește
    în anul back-test-ului, iar textul publicat spune „nu a deținut”, e numărată separat (`slots_expected`).
14. **(24.10) Motivele gap-urilor, în română:** direcția dovezii apare ca „în scădere”/„în creștere”, nu
    „down”/„up”; variația sub prag se scrie cu virgulă („-0,26 %”), împreună cu pragul.
15. **(24.10) Teste noi:** SCR în creștere (cauza „scădere” cade), variație sub prag, unități în milioane,
    antete cu anul, etichete în coloana A, MCR ca text, diversificare introdusă negativ.

## Bug-uri găsite și reparate

| # | Ce | Cum s-a văzut | Reparație |
|---|---|---|---|
| 1 | Nivelul 1 și 2 apăreau în draft ca `{own_funds_t1}`: regex-ul sloturilor nu accepta cifre în nume | prima rulare, citind draftul; verificarea „fiecare sumă are sursă” număra 5 sume în loc de 7 | `[a-z0-9_]+` în `SLOT` |
| 2 | Termenul interzis „reasigurare” apărea în textul legal („asigurare și reasigurare”): alarmă falsă | verificarea `text:fara-reinsurance-improved-ratio` a eșuat pe datele reale | termenii restrânși la „program(ul/ului) de reasigurare” |
| 3 | Verificarea de asemănare cu Dunărea se declanșa pe titlul standard al raportului | 3 secvențe comune, toate din antet | verificarea rulează doar pe corpul secțiunii |
| 4 | Clauza de comparație SCR conținea anul greșit (expresie greșită în `resolve_comparison`) | citind codul | anul transmis explicit |
| 5 | O cauză lipsă în interiorul comparației nu era trecută în lista de gap-uri | citind codul | `Slot` cu text și motiv; gap-ul parțial e raportat |
| 6 | Lipsa `registru_2024.xlsx` oprea toată rularea (back-test-ul ridica eroare) | rularea pe mutații | back-test-ul se sare, cu motivul în `backtest_2024.md` |
| 7 | SCR = 0 pe ambele foi ar fi dat împărțire la zero la rată | citind codul după mutații | gardă: SCR devine nesigur, rata gap |
| 8 | Citirea raportului de anul trecut accepta „propoziția întreagă e un gap”; căutarea putea potrivi un gap din altă propoziție, iar cifra reală nu mai era găsită | recitirea codului | alternativa scoasă; gap-urile sunt acceptate doar la nivel de slot |
| 9 | Două figuri găsite în aceeași celulă (de exemplu SCR căutat pe SCR_module când lipsește foaia Capital) făceau ca verificarea „SCR pe două foi” să treacă fără să dovedească nimic | analiza mutațiilor | verificarea nu rulează, iar figurile devin nesigure |
| 10 | Motivele gap-urilor repetau tot textul și conțineau stări în engleză („uncertain”) | citind draftul pe variante stricate | rata spune doar de ce figură depinde; stări în română; verificarea între foi arată ambele valori formatate, cu celula |
| 11 | Un test aștepta ca SCR să fie citit din foaia reală când copia veche avea același titlu | testul a picat | programul avea dreptate (ambiguitate → gap); aserțiunea corectată |

## De ținut minte

- Orice mutație nouă care strică programul devine test în `tests/test_broken_workbooks.py`.
- Orice schimbare de comportament se notează aici, la „Ce s-a schimbat față de plan” sau „Bug-uri”.

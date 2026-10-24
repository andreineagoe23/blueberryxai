# Back-test pe 2024

## 1. Catalogul pe registru_2024.xlsx față de secțiunea E din raport_2024.txt

Programul rulează pe registrul 2024 și compară fiecare cifră pe care ar scrie-o cu cifra publicată.

| Slot | Publicat | Calculat de program | Rezultat |
|---|---|---|---|
| own_funds_total | 284,6 mil. lei | 284,6 mil. lei | ok |
| own_funds_t1 | 251,3 mil. lei | 251,3 mil. lei | ok |
| own_funds_t2 | 33,3 mil. lei | 33,3 mil. lei | ok |
| own_funds_t3 | nul | gap (lipsă) | așteptat: în registru_2024.xlsx rândul nu există, iar textul publicat se sprijinea pe lipsa lui; în 2025 programul cere un rând explicit, altfel lasă loc de completat |
| own-funds-legal-basis | text identic | — | ok |
| evidence__dividends | 12,0 mil. lei | — | sursă documentară, nu din registru: nu se compară |
| clause__dividend_policy | «, conform politicii de dividende aprobate de Consiliul de Administrație» | — | text, nu cifră (se verifică prin dovezi) |
| scr | 151,9 mil. lei | 151,9 mil. lei | ok |
| comparison__scr__direction | în creștere | în creștere | ok |
| comparison__scr__prior | 140,2 mil. lei | 140,2 mil. lei | ok |
| comparison__scr__cause | «ca urmare a creșterii volumului de prime brute subscrise la 412,4 mil» | — | text, nu cifră (se verifică prin dovezi) |
| solvency_ratio | 187,4 % | 187,4 % | ok |
| mcr | 45,6 mil. lei | 45,6 mil. lei | ok |
| coverage__mcr | «a fost acoperită integral» | — | text, nu cifră (se verifică prin dovezi) |
| metoda de calcul a SCR | text identic | — | ok |

## 2. mapping_2024.toml pe propriul an

Fiecare intrare e citită din registru_2024.xlsx (cu unitatea foii) și comparată cu textul din raport_2024.txt, pe număr întreg, nu pe subșir.

| Text | Apariția | Celula | Rezultat | Detaliu |
|---|---|---|---|---|
| 412,4 | 1 | Prime!C10 | ok | reproduce «412,4» |
| 168,2 | 1 | Prime!C5 | ok | reproduce «168,2» |
| 40,8 | 1 | Prime!C5 | ok | reproduce «40,8» |
| 121,9 | 1 | Prime!C6 | ok | reproduce «121,9» |
| 29,6 | 1 | Prime!C6 | ok | reproduce «29,6» |
| 74,3 | 1 | Prime!C7 | ok | reproduce «74,3» |
| 18,0 | 1 | Prime!C7 | ok | reproduce «18,0» |
| 29,4 | 1 | Prime!C8 | ok | reproduce «29,4» |
| 7,1 | 1 | Prime!C8 | ok | reproduce «7,1» |
| 18,5 | 1 | Prime!C9 | ok | reproduce «18,5» |
| 4,5 | 1 | Prime!C9 | ok | reproduce «4,5» |
| 198,7 | 1 | Daune!C5 | ok | reproduce «198,7» |
| 18.420 | 1 | Daune!C6 | ok | reproduce «18.420» |
| 352,8 | 1 | Investitii!C5 | ok | reproduce «352,8» |
| 12,6 | 1 | Investitii!C7 | **greșit** | celula Investitii!C7 («Pondere titluri de stat») dă «0,0», nu «12,6»; celula care dă «12,6»: Investitii!C6 «Venituri din investiții» |
| 78,4 | 1 | Investitii!C7 | ok | reproduce «78,4» |
| 6,2 | 1 | Investitii!C8 | ok | reproduce «6,2» |
| 97,6 | 1 | SCR_module!C5 | ok | reproduce «97,6» |
| 58,3 | 1 | SCR_module!C6 | ok | reproduce «58,3» |
| 12,1 | 1 | SCR_module!C7 | ok | reproduce «12,1» |
| 12,4 | 1 | SCR_module!C10 | ok | «12,4» apare de 3 ori ca subșir, dar de 1 ori ca număr întreg; o căutare pe subșir ar nimeri în interiorul altui număr |
| 28,5 | 1 | SCR_module!C8 | ok | reproduce «28,5» |
| 192,1 | 1 | Provizioane!C7 | ok | reproduce «192,1» |
| 182,3 | 1 | Provizioane!C5 | ok | reproduce «182,3» |
| 9,8 | 1 | Provizioane!C6 | ok | reproduce «9,8» |
| 284,6 | 1 | Capital!C7 | ok | reproduce «284,6» |
| 251,3 | 1 | Capital!C5 | ok | reproduce «251,3» |
| 33,3 | 1 | Capital!C6 | ok | reproduce «33,3» |
| 151,9 | 1 | Capital!C9 | ok | reproduce «151,9» |
| 140,2 | 1 | Capital!D9 | ok | reproduce «140,2» |
| 412,4 | 2 | Prime!C10 | ok | reproduce «412,4» |
| 187,4 | 1 | Capital!C11 | ok | reproduce «187,4» |
| 45,6 | 1 | Capital!C10 | ok | reproduce «45,6» |

Rezultat: 32 din 33 intrări reproduc textul; 1 greșite; 1 corecte doar dacă se caută pe număr întreg.

# Audit: capcane și erori în materialele assessmentului

Document de lucru (nu face parte din livrabil). Verificat programatic pe 23.10.2026:
fiecare celulă din ambele registre (inclusiv foi ascunse, formule și valori cache), XML-ul brut
din xlsx/docx, toate cele 33 de intrări din `mapping_2024.toml` față de text și registru,
rotunjirile (Decimal half-up vs half-even vs float) și codificarea fișierelor text.

**Severitate**
- **C (critic)**: o cifră greșită sau o frază nesusținută ajunge în raport dacă nu e prinsă.
- **M (major)**: sistemul se strică sau ia o decizie în tăcere.
- **m (minor)**: fragilitate, de notat în DESIGN.md.

**Secț.** = secțiunea din raport afectată. **E** = intră în felia de cod.

---

## 1. Registrul 2025: structură schimbată („coleg nou de la contabilitate”)

| ID | Sev | Secț. | Ce | Unde / dovadă | Ce trebuie să facă sistemul |
|---|---|---|---|---|---|
| R1 | C | E, C, D, A | **Unitatea s-a schimbat din lei în mii lei** pe foile Capital, SCR_module, Provizioane, Daune. Prime și Investitii au rămas în lei. Antetul mappingului 2024 spune „Valorile din registru sunt în lei”, ceea ce nu mai e adevărat. | `Capital!A2` = „Valori în mii lei”; `Daune!A2` = „Valori în mii lei, cu excepția numărului de dosare” | Citește unitatea **per foaie** (A2), nu din mapping și nu global. Dacă unitatea lipsește sau nu e recunoscută, nu se folosește valoarea. Verificare de plauzibilitate: ordinul de mărime față de N-1. |
| R2 | C | E | **Rânduri mutate**: s-a inserat „nivel 3” pe rândul 7. Total: C7 → **C8**; SCR: C9 → **C10**; MCR: C10 → **C11**; rata: C11 → **C12**. | foaia Capital, 2024 vs 2025 | Localizare după **etichetă** (coloana B) + foaie + antet coloană („31.12 an curent”), nu după coordonată. Cu mappingul 2024 aplicat orbește: „total” ar citi nivel 3 = 0, „SCR” ar citi un rând gol, „MCR” ar citi SCR. |
| R3 | C | E | **Foaie ascunsă `Capital_vechi`** cu cifrele 2024 (251,3 / 33,3 / 284,6 / 151,9 / 45,57) la coordonatele vechi C5–C10, în lei. A1 = „NU SE FOLOSEȘTE (copie 2024)”. Etichete scurte („nivel 1”, „total”). | `workbook.xml`: `state="hidden"`, prima foaie | Ignoră foile ascunse (sau orice foaie marcată „nu se folosește”) și **raportează** că le-a ignorat. Detectare suplimentară: valoare identică cu N-1 = suspect (vezi V2). |
| R4 | M | E, D | **Totalurile sunt formule**: `Capital!C8 = C5+C6+C7`, `Provizioane!C7 = C5+C6`, `D7 = D5+D6`. Cache-ul există aici (293.699,3; 207.318,1), dar fișierul e generat cu openpyxl (`creator=openpyxl`, `fullCalcOnLoad="1"`). O altă versiune poate avea formula **fără valoare cache**, deci `data_only=True` dă `None`. | sheet7.xml `<f>C5+C6+C7</f><v>293699.3</v>` | Citește atât formula, cât și cache-ul. Dacă lipsește cache-ul, evaluează formulele simple (sume) sau recalculează din componente, cu provenance „calculat”. Dacă există cache, compară-l cu recalcularea; diferență = conflict. |
| R5 | C | E | **Diversificarea și-a schimbat semnul**: 2024 = −28.500.000 („Diversificare (valoare negativă)”); 2025 = +22.431,9 („Efect de diversificare (se scade)”). | `SCR_module!B8/C8` | Semnul se interpretează din etichetă/config, nu se presupune. Verificare: module − diversificare = SCR de bază (135.493,0). Cu adunare oarbă rezultă 180,4. Formatul `mil_lei_1_abs` salvează textul, dar nu și verificarea. |
| R6 | m | E | **Nivel 3 apare explicit** (`Capital!C7 = 0`); în 2024 rândul nu exista. | foaia Capital | Fraza „nu a deținut fonduri proprii de nivel 3” e acum **susținută de o celulă** (în 2024 era susținută de absența rândului). Dacă altă versiune are nivel 3 > 0, fraza trebuie să se schimbe. |
| R7 | m | E | **Coloana E nouă**, cu text: `Capital!E11 = „în lucru, actuariat”`. | foaia Capital, dimensiune A1:E12 | Citește notele din coloanele vecine ca **motiv** pentru gap. |
| R8 | m | toate | Coloana D („an anterior”) e completată **inconsecvent**: există la Capital!D10 și Provizioane D5–D7, lipsește în rest. | — | Nu te baza pe coloana D pentru comparații. Sursa pentru N-1 este registrul N-1 sau raportul N-1, iar coloana D servește doar la verificare încrucișată. |

## 2. Valori: lipsă, vechi, contradictorii

| ID | Sev | Secț. | Ce | Dovadă | Ce trebuie să facă sistemul |
|---|---|---|---|---|---|
| V1 | C | E, Sinteză | **MCR lipsește**: `Capital!C11` gol; `E11` = „în lucru, actuariat”. Nota actuarială confirmă: „Calculul cerinței de capital minim este în curs de finalizare și va fi transmis separat.” | registru + docx | `[de completat: MCR nu este disponibil; celula Capital!C11 este goală („în lucru, actuariat”), iar nota funcției actuariale din 02.02.2026 arată că se transmite separat]`. Cade și fraza „**a fost acoperită integral**”, care nu se poate afirma fără MCR. **Momeală:** în 2024, MCR = exact 30,0 % din SCR (45,57 / 151,9), deci ar fi tentant să calculezi 0,30 × 148,8 = 44,6. Interzis: e o estimare nesusținută. |
| V2 | C | E, Sinteză | **Rata de solvabilitate e veche**: `Capital!C12 = 1,874` (187,4 %), **identică cu 2024**. Calculul din aceeași foaie dă 293.699,3 / 148.763,2 = **197,427… % → 197,4 %**. | registru | **Conflict explicit, nu alegere tăcută.** Detectori: (a) ratio ≠ OF / SCR peste toleranță; (b) valoare identică cu N-1 = suspect. Rezolvare doar prin decizie în config (de ex. „folosește valoarea calculată, sursa Capital!C8/C10, motiv: C12 e copiată din 2024”) sau gap. Este exact tipul de eroare găsit de auditor anul trecut. |
| V3 | C | A (indirect E) | **Prime RCA greșite în registru**: `Prime!C6 = 142.017.800`; situațiile financiare auditate (Nota 4) dau **124.017.800**, cu cifre inversate. Suma liniilor din registru = 456.912.400 ≠ totalul de 438.912.400. Suma din situațiile financiare = 438.912.400, deci se potrivește. | registru vs PDF p.1 | Verificarea „suma liniilor = total” prinde eroarea. Verificarea registru ↔ situații auditate o localizează. Decizia (auditul are prioritate pentru cifre contabile) se ia în config. Totalul de 438,9 e confirmat de ambele surse. |
| V4 | M | D | **Coloana „an anterior” din Provizioane nu se potrivește cu raportul publicat 2024**: D5 = 184.100 (vs 182,3 publicat), D7 = 193.900 (vs 192,1). D6 = 9.800 se potrivește. | registru 2025 vs raport 2024 | Retratare sau eroare. Nu se poate decide din materiale, deci se semnalează. Nu se folosește 184,1 în text. |
| V5 | m | E | **Cross-check-uri care trec**: `Capital!C10` (148.763,2) = `SCR_module!C11`; `Capital!D10` (151.900) = SCR 2024 publicat (151,9); SCR de bază + operațional = SCR; nivel 1 + nivel 2 + nivel 3 = total. | — | Trebuie rulate și raportate ca dovadă (inclusiv cele care trec). |
| V6 | m | A | Ponderea acțiunilor listate în 2025 = 0 (`Investitii!C8`), consecvent cu nota actuarială (vânzare integrală în T3). | — | Confirmă narativul nou; fraza din 2024 cu 6,2 % trebuie rescrisă. |

## 3. Mapping 2024 (`mapping_2024.toml`): nu e de încredere

| ID | Sev | Ce | Dovadă | Implicație |
|---|---|---|---|---|
| P1 | C | **Celulă greșită**: „12,6” (venituri din investiții) e mapat la `Investitii!C7`, care conține ponderea titlurilor de stat (0,784) și dă „0,0”. Corect: **C6** (12.640.000). | rularea mappingului pe registrul 2024 | Mappingul trebuie **validat** pe anul lui (registrul N-1 trebuie să reproducă exact textul N-1) înainte să fie folosit. Așa se prind erorile din mapping. |
| P2 | M | **Capcană de subșir**: textul „12,4” (riscul operațional) apare de 3 ori ca subșir, de două ori în interiorul lui „412,4”. Cu `str.find` simplu, „occurrence = 1” lovește **prima de prime brute**. | regex cu limite de token: 1 apariție reală | Potrivire pe **token numeric întreg**, nu subșir. Mai bine: șablon cu ID-uri (sloturi), nu ancorare pe text. |
| P3 | M | **Cifre nemapate** în raportul 2024: `412` angajați, `214,6` rezerve statutare (din situațiile financiare), **`12,0` dividende** (din situațiile financiare, în secțiunea E), anii (2024 ×10, **2023**), referințele legale (2015/35, 237/2015, 1 ianuarie 2016), „cinci” membri (în litere). | scanare tokeni numerici | Mappingul acoperă doar registrul. Documentele nu au mapping, deci trebuie un catalog de figuri care include și sursele documentare (cu pagina). **Anii trebuie avansați**: „la sfârșitul anului 2023” devine „2024”. |
| P4 | m | Mappingul e ancorat pe **textul cifrei** + `occurrence`, deci se strică imediat ce cifrele se schimbă. Mappingul 2025 nu poate fi „același fișier cu alte cifre”. | design | Mappingul 2025 trebuie **generat** de sistem (ID figură → celulă + motiv), nu editat de mână. |
| P5 | m | „412,4” apare de 2 ori (A.2 și E.2, ca explicație a SCR). | occurrence 2 | Aceeași figură în mai multe locuri = un singur fapt, mai multe sloturi. |

Verificat: celelalte 31 de intrări reproduc exact textul 2024 (inclusiv ponderile calculate cu Decimal half-up).

## 4. Documente-sursă

| ID | Sev | Sursă | Ce conține / capcană | Ce trebuie să facă sistemul |
|---|---|---|---|---|
| D1 | – | `situatii_financiare_2025_extras.pdf` (1 pagină, text extractibil, ReportLab) | Auditor Auditex Consult, opinie fără rezerve din 12.03.2026. Nota 4 prime (RCA 124.017.800). Rezerve tehnice brute 231.842.500 (2024: 214.600.000, egal cu raportul). Profit net 31,4 (27,9). **Dividende plătite (15.000.000)**, în paranteză = flux negativ. Nota 21: **număr mediu** de angajați 437. | Parsare: separator de mii „.”, paranteze = negativ. Citare cu pagina (p.1, Nota X). |
| D2 | M | idem | Numărul mediu de angajați (437) ≠ angajați **la 31 decembrie** (2024: 412). Altă măsură. | Nu se substituie. A.1: `[de completat: numărul de angajați la 31.12.2025; situațiile financiare dau doar media anuală (437)]` sau se reformulează explicit ca „număr mediu”, cu decizie umană. |
| D3 | – | `proces_verbal_AGA_2025-04-24.txt` | Dividende **15.000.000 lei** din profitul 2024, aprobate de AGA, plătibile până la 30.06.2025. Politica de dividende aprobată de CA în 2023 rămâne neschimbată. | **Două surse concordă** (AGA + flux de numerar din situațiile financiare), deci E.1: „În cursul anului 2025, Societatea a plătit dividende de 15,0 mil. lei, conform politicii de dividende aprobate de Consiliul de Administrație.” Fraza e susținută. |
| D4 | M | `proces_verbal_CA_2025-02-18_scanat.pdf` | **Scan, fără text** (imagine, deci e nevoie de OCR). Numirea dlui Radu Ionescu; Consiliul crește la **6 membri**; „produce efecte de la data **avizării ASF**”. | Nu există dovadă a avizării, deci B.1: `[de completat: numărul de membri ai CA la 31.12.2025; numirea din 18.02.2025 produce efecte de la avizarea ASF, care nu e documentată]`. Textul obținut prin OCR se marchează ca „necesită verificare umană”. |
| D5 | – | `nota_functia_actuariala_2026-02-02.docx` | SCR **a scăzut**, „în principal ca urmare a scăderii riscului de piață”; acțiunile listate vândute integral în T3, banii mutați în titluri de stat. Riscul de subscriere a crescut, mai ales la incendiu. **Reasigurarea a fost reînnoită la 01.01.2025 în aceleași condiții, fără efect asupra capitalului.** MCR în curs. Formula standard, fără parametri specifici proprii. | Este **singura sursă de explicații** („ca urmare a”). Metadate implicite (python-docx, 2013), fără conținut ascuns, fără track changes și fără comentarii (verificat în XML). Data notei (02.02) e anterioară opiniei de audit (12.03), dar nota nu conține cifre, deci nu apare conflict. |
| D6 | C | `email_director_financiar.txt` | Presiune de la client, cu 3 cereri care încalcă regulile (vezi secțiunea 5). | — |
| D7 | C | `raport_Asigurari_Dunarea_2024_extras.txt` | Textul altei companii. Conține tocmai narativul dorit de CFO („program de reasigurare optimizat… reducerea SCR”) și un „plan care se activează automat”. | **Nu se folosește nicio formulare** (regula 4) și nicio afirmație despre Carpați nu se deduce de aici. Ideal: verificare automată de similaritate (n-grame) între draft și documentele altor companii. |

## 5. Emailul CFO-ului (inginerie socială / presiune)

| # | Cerere | Verdict | Regula |
|---|---|---|---|
| 1 | Fișierul e făcut de un coleg nou, „aceleași celule… poate arată puțin diferit” | **Fals.** Celulele s-au mutat, iar unitățile s-au schimbat (R1, R2). Informație utilă: confirmă riscul. | – |
| 2 | „Dacă lipsește vreo cifră, puneți-o pe cea de anul trecut” | **Refuz.** MCR 45,6 din 2024 ar ajunge în raport. | Regula 1 + regula domeniului (gap vizibil > cifră greșită) |
| 3 | „Să apară clar că rata s-a îmbunătățit datorită noului program de reasigurare” | **Refuz.** Nota actuarială contrazice direct („aceleași condiții”, fără efect). În plus, rata din registru (187,4 %) arată „neschimbat”. | Regula 2 (explicații nesusținute) |
| 4 | „Luați formulări de la Asigurări Dunărea” | **Refuz.** | Regula 4 |
| 5 | „Pentru dividende… situațiile financiare auditate” | **Ok**, sursă validă (D1, D3). | – |

Pentru DESIGN.md: refuzurile trebuie să fie **vizibile și justificate** (raport de probleme), nu tăcute. CFO-ul semnează, deci trebuie să vadă de ce i s-a refuzat cererea.

## 6. Afirmații din 2024 care nu mai sunt adevărate (direcție, explicație, fapte)

| ID | Sev | Secț. | Text 2024 | Realitate 2025 | Acțiune |
|---|---|---|---|---|---|
| T1 | C | **E.2** | „SCR… **în creștere** față de 140,2… **ca urmare a creșterii volumului de prime brute subscrise** la 412,4” | SCR **scade**: 151,9 → 148,8 (−3,1 mil.; −2,1 %). Cauza, conform notei actuariale: **scăderea riscului de piață** (41,9 vs 58,3). Primele cresc, dar nu ele explică direcția SCR. | Direcția se **calculează** (comparare N vs N-1 pe valori nerotunjite). Explicația vine **doar** din registrul de dovezi (nota actuarială); altfel e gap. Fraza „ca urmare a primelor” dispare. |
| T2 | M | C | „Expunerea pe riscul de piață provine în principal din acțiunile listate” | Acțiunile listate = 0 % (vândute în T3) | Fals. Se rescrie sau se lasă gap (nu e clar din ce provine acum riscul de piață; probabil din titlurile de stat, dar **nesusținut**). |
| T3 | – | C | „Riscul de subscriere este cea mai mare componentă, urmat de riscul de piață” | 104,2 > 41,9 > 11,8, deci **încă adevărat** | Exemplu bun: o afirmație de ordine re-verificată automat. |
| T4 | M | A.3 | „acțiunile listate la BVB 6,2 %” | 0,0 % | Fraza trebuie schimbată, nu doar cifra („0,0 % acțiuni listate” e stângaci). |
| T5 | M | A.2 | „412,4 mil. lei, în creștere față de anul anterior” | 438,9 vs 412,4, deci tot **în creștere** (+6,4 %) | Direcția recalculată, nu copiată. |
| T6 | M | B.1 | „cinci membri”, „cel puțin o dată pe trimestru” | 6 membri condiționat de avizarea ASF; frecvența ședințelor nu e documentată pentru 2025 | Gap / confirmare umană. Textul static (guvernanță) are nevoie de **reconfirmare anuală**, nu de copiere. |
| T7 | M | A.1 | „La 31 decembrie 2024… 412 angajați” | doar media anuală 437 | Vezi D2. |
| T8 | – | A.1 | Auditor Auditex Consult | confirmat de situațiile financiare 2025 | Ok, cu sursă. |
| T9 | M | Sinteză | „au acoperit integral atât SCR, cât și MCR”; „nu au existat situații de neconformitate” | SCR acoperit (197,4 % calculat); MCR necunoscut; nicio sursă despre neconformitate în 2025 | Gap-uri. |
| T10 | m | E.1 | Referințele legale (Reg. 2015/35, Legea 237/2015, de la 1 ianuarie 2016) | text static, fără sursă în materiale | Bloc de text fix, aprobat explicit de om în config (o dată, cu motiv). |
| T11 | M | toate | Ani: „2024” → „2025”, „sfârșitul anului **2023**” → „**2024**” | — | Anul de raportare e parametru și se avansează sistematic; anii din referințele legale (2015, 2016) **nu** se avansează. |
| T12 | – | E | Fondurile proprii cresc: 284,6 → 293,7 (+9,1) | direcția e calculabilă | **Nicio sursă nu explică creșterea**, deci se poate scrie „au crescut”, dar fără „ca urmare a”. |
| T13 | M | E | Rata: 187,4 → 197,4 (dacă e acceptată valoarea calculată) | crește aritmetic (OF ↑, SCR ↓) | „S-a îmbunătățit” e o concluzie de calcul. Cauza „reasigurare” e falsă (T1, D5). |

## 7. Rotunjire și format

| ID | Sev | Ce | Exemplu concret |
|---|---|---|---|
| F1 | C | **Totalul nu e suma valorilor rotunjite**: nivel 1 262,4 + nivel 2 31,2 = **293,6**, dar totalul = **293,7** (293,6993). Cititorul vede o „eroare” care nu e eroare; totalul se ia din sursă (regula 5). | E.1 2025 |
| F2 | M | Același efect în 2024: 168,2 + 121,9 + 74,3 + 29,4 + 18,5 = 412,3 vs total 412,4. | A.2 |
| F3 | M | **Rotunjire o singură dată, pe valoarea nerotunjită**: rata = 293.699,3 / 148.763,2, nu 293,7 / 148,8. Aici ambele dau 197,4 (coincidență), dar regula se testează. | E.2 |
| F4 | m | Nicio valoare actuală nu e exact pe .x5 după scalare, deci half-up = half-even = float aici. **Pe altă versiune de registru poate fi.** 412.350.000 (2024) e cazul-limită: half-up dă 412,4. Doar `Decimal` + `ROUND_HALF_UP` e sigur; testele trebuie să includă un caz .x5. | — |
| F5 | m | Format: `284,6 mil. lei`; `187,4 %` (spațiu înainte de %); `18.420`; virgulă zecimală. Valoarea negativă (diversificarea) apare fără semn în text. 0 apare ca „0,0 %”, ceea ce semantic sună prost (T4). | — |
| F6 | m | Daune 2025 în mii lei cu zecimale (231.450,6) dau 231,5 mil. lei; numărul de dosare (21.037) **nu** se scalează („cu excepția numărului de dosare”). | Daune!A2 |
| F7 | m | Fișierele text sunt UTF-8, fără BOM, fără CRLF, fără NBSP, cu diacritice corecte (ș/ț cu virgulă, nu sedilă). Niciun truc de encoding. | verificat |

## 8. Ce probabil se schimbă în „cealaltă versiune” a `registru_2025.xlsx` (testul lor ascuns)

Programul trebuie să reziste, **fără modificări de cod**, la:
- MCR completat (atunci fraza „acoperită integral” devine posibilă, dar doar dacă OF ≥ MCR; atenție, MCR se acoperă cu fonduri proprii eligibile pentru MCR, unde nivel 2 e limitat, iar asta nu e în date → se semnalează);
- rata corectată în C12 (conflictul dispare; trebuie să treacă fără decizie);
- rata greșită altfel sau SCR diferit între `Capital` și `SCR_module`;
- rânduri mutate din nou, foi redenumite sau reordonate, foaie ascunsă vizibilă sau redenumită;
- unități înapoi în lei (sau în mil. lei), unitate lipsă;
- formula de total fără cache;
- nivel 3 > 0; nivel 2 sau 1 lipsă;
- etichete ușor diferite (diacritice, majuscule, spații) → normalizare + potrivire tolerantă, dar **ambiguitatea = eroare, nu alegere**;
- valori text în loc de numere („148.763,2” ca string).

Principiu: fiecare figură are status `ok | conflict | lipsă | nesigur`, iar textul folosește doar `ok` sau `rezolvat-prin-decizie`.

## 9. Ce poate intra în secțiunea E 2025 (pe datele actuale)

| Figură | Valoare | Sursă | Status |
|---|---|---|---|
| Fonduri proprii eligibile SCR | 293,7 mil. lei | Capital!C8 (formulă; cache 293.699,3 = C5+C6+C7) | ok |
| Nivel 1 | 262,4 mil. lei | Capital!C5 | ok |
| Nivel 2 | 31,2 mil. lei | Capital!C6 | ok |
| Nivel 3 | 0 → „nu a deținut” | Capital!C7 | ok |
| Dividende plătite în 2025 | 15,0 mil. lei | situațiile financiare p.1 (flux de numerar) + PV AGA 24.04.2025 | ok (2 surse concordă) |
| SCR 2025 | 148,8 mil. lei | Capital!C10 = SCR_module!C11 | ok |
| SCR 2024 (comparație) | 151,9 mil. lei | Capital!D10 = raport 2024 = registru 2024 Capital!C9 | ok |
| Direcția SCR | scădere | calcul 148.763,2 < 151.900 | ok |
| Explicația SCR | riscul de piață | nota actuarială 02.02.2026, par. 1 | ok (document) |
| Rata de solvabilitate | 197,4 % calculat vs 187,4 % în C12 | Capital!C8 / C10 vs C12 | **conflict**, cere decizie |
| MCR | — | Capital!C11 gol | **lipsă**, deci gap |
| MCR „acoperită integral” | — | — | **nesusținut**, deci gap |
| Formula standard, fără parametri specifici proprii | text | nota actuarială, ultimul paragraf | ok (document) |
| Referințe legale E.1 | text fix | — | decizie umană (config) |

## 10. Presupuneri de notat în DESIGN.md

1. Situațiile financiare auditate au prioritate față de registru la cifrele contabile (prime, dividende, rezerve statutare). Registrul are prioritate la cifrele Solvabilitate II. Conflictele se raportează oricum.
2. Foile ascunse nu sunt surse.
3. „31.12 an curent” = 31.12.2025 (anul se deduce din numele fișierului sau din config, nu din celulă, pentru că registrul nu conține anul).
4. Nota actuarială e o sursă acceptabilă pentru explicații (e funcție-cheie, adresată CA), deși nu e auditată.
5. Rata de solvabilitate = OF eligibile SCR / SCR, recalculabilă din registru; o valoare introdusă care diferă de calcul e conflict.
6. Textul static (referințe legale, guvernanță) se reconfirmă anual de un om; sistemul nu îl poate verifica.

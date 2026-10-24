# Rezumat pentru interviu: BlueberryX, SFCR secțiunea E

Document personal de repetat. Nu intră în zip. Cifrele sunt cele de pe 24.10.2026: 48 de teste,
3 commit-uri pe `main`, DESIGN.md în 4 pagini.

---

## 1. Tema într-un paragraf

Asigurări Carpați (fictivă) publică anual SFCR-ul, iar acum îl actualizează de mână, în 6 săptămâni. Anul
trecut a ajuns la ASF o cifră greșită. BlueberryX vrea un sistem care face **roll-forward**: din raportul de
anul trecut și datele de anul acesta, produce draftul de anul acesta, pe care oamenii îl revizuiesc. Regula de
aur: **o cifră greșită sau o frază nesusținută e mult mai rea decât un gol vizibil** (`[de completat: motiv]`).

Livrabile:
1. `DESIGN.md`, maximum 4 pagini, cu diagramă: memo pentru CFO și CTO.
2. Cod doar pentru **secțiunea E** (fonduri proprii, SCR, MCR, rata de solvabilitate): o comandă din `date/`,
   cu tot ce produce în `output/`. **Ei îl rulează neschimbat pe alt `registru_2025.xlsx`.**
3. `ai/`: `AI.md` (o pagină) și conversațiile brute.

Zip-ul `andrei_neagoe.zip` conține: `README.md`, `DESIGN.md`, `ai/`, `config/`, `output/`, `src/`, `tests/`.
**Nu intră** `notes/`, `date/`, `.venv/` sau cache-urile. Repo-ul public:
https://github.com/andreineagoe23/blueberryxai (datele sunt fictive).

---

## 2. Rezultatul pe datele reale (de știut pe de rost)

| Figură | Valoare în draft | Sursa | Observații |
|---|---|---|---|
| Fonduri proprii eligibile | **293,7 mil. lei** | Capital!C8 (formula C5+C6+C7, 293.699,3 mii lei) | totalul se ia din sursă, nu se adună rotunjitele (262,4 + 31,2 = 293,6 ≠ 293,7) |
| Nivel 1 / Nivel 2 | 262,4 / 31,2 | Capital!C5 / C6 | |
| Nivel 3 | „nu a deținut” | Capital!C7 = 0 | rândul e nou în 2025 |
| Dividende plătite | **15,0** | situațiile financiare p. 1, „(15.000.000)”, plus PV AGA punctul 3 | două surse concordă |
| SCR | **148,8** | Capital!C10 = SCR_module!C11 | |
| Comparația | „în scădere față de 151,9” | registru 2024 C9 = coloana „an anterior” D10 = raportul 2024 | −2,1 %, peste pragul de 0,5 % |
| Cauza | „în principal ca urmare a scăderii riscului de piață” | nota actuarială, paragraful 1, citat verbatim | riscul de piață 58,3 → 41,9 |
| Rata | **197,4 %** | calculată: C8 / C10 | celula C12 = 187,4 % = identică cu 2024, deci conflict, rezolvat prin decizia `solvency-ratio-2025` |
| MCR | **gap** | Capital!C11 gol, E11 „în lucru, actuariat” | nota actuarială: „se transmite separat”; fără „acoperită integral” |

Restul:
- Rulare: 1 loc de completat, 1 figură decisă prin config, 36 de verificări (33 trecute, 2 eșuate, 1 care nu
  a putut rula: coridorul MCR).
- Back-test 2024: 10 sloturi reproduse și 1 diferență așteptată (nivelul 3, pentru că în 2024 rândul nu
  exista).
- Mapping 2024: 32 din 33 de intrări corecte. **„12,6” e mapat greșit** (Investitii!C7 în loc de C6), iar
  **„12,4” apare de 3 ori ca subșir** (de două ori în „412,4”) și o singură dată ca număr întreg.

---

## 3. Fluxul programului

```
main.py
  └─ pipeline.analyse(an, folder, cfg)
       1 workbook.load        registrul N și N-1: foi vizibile, antete, unități, rânduri cu etichete
       2 locate (catalog)    fiecare figură → exact o celulă + motiv, altfel missing/uncertain
       3 checks.compare_prior identic cu N-1? ordin de mărime?
         checks.run_checks    sume, coridor MCR
         checks.derive        rata = OF / SCR față de cea raportată
       4 decisions.apply      decizii legate de valorile observate
       5 evidence.verify_all  fiecare citat regăsit verbatim în document
       6 compose.published    citește cifrele din raportul de anul trecut, cu același șablon
         compose.resolve_comparison  valoarea N-1 din ≥2 surse, direcția, cauza din dovezi
       7 compose.compose      textul secțiunii E, cu sloturi; gap scurt în draft
       8 _check_draft         fiecare sumă are sursă; fără termeni interziși; fără text Dunărea
  └─ backtest.run         același pipeline pe 2024 + validarea mappingului 2024
  └─ outputs.write_all    7 fișiere, deterministe
```

Ideea centrală: **catalogul spune CE e o figură (eticheta, foaia, tipul), nu UNDE e (celula)**. Celula se
găsește la fiecare rulare, cu motivul alegerii. Mappingul vechi doar testează catalogul.

**Stările unei figuri:** `ok` < `decided` < `uncertain` < `conflict` < `missing`. `Fact.flag()` poate doar să
coboare starea, niciodată să o ridice. În text intră doar `ok` și `decided`; orice altceva devine gap.

---

## 4. Fișier cu fișier

### `src/main.py`
- Comanda. Cu `argparse`: `--input` (implicit folderul curent, adică `date/`), `--config` (implicit
  `config/` de lângă `src/`), `--out` (implicit `output/` din rădăcină).
- Rulează `analyse` pe anul din `run.toml`, apoi back-test-ul, apoi scrie fișierele.
- Afișează un rezumat de o linie.
- Exit 0 dacă fișierele s-au scris (gap-urile nu sunt erori); exit 2 dacă lipsește registrul anului (`InputError`).

### `src/sfcr/pipeline.py`
Analiza unui an, folosită și de rularea principală, și de back-test.
- `load_config`: citește cele 4 fișiere TOML.
- `input_name`: numele fișierelor din șabloane (`registru_{year}.xlsx`).
- `analyse`:
  - încarcă registrul N (obligatoriu) și N-1 (opțional);
  - localizează toate figurile în ambele;
  - rulează verificările și aplică deciziile;
  - verifică dovezile;
  - transformă dovezile cu `figure` (dividendele) în figuri cu sursă documentară;
  - adaugă o notă dacă MCR apare în registru, deși nota actuarială spune „în curs”;
  - citește raportul de anul trecut, rezolvă comparațiile, compune draftul.
- `_check_draft`, verificări pe textul final:
  - fiecare „X mil. lei” / „X %” din text vine dintr-o figură plasată;
  - niciun `forbidden_terms` din cererile respinse;
  - nicio secvență comună de 6 cuvinte cu raportul Dunărea (doar pe corpul secțiunii, nu pe titlul
    standard).

### `src/sfcr/workbook.py`: extragerea, fără să știe ce figură e care
- `normalize`: litere mici, fără diacritice (ș/ş, ț/ţ la fel), punctuația înlocuită cu spațiu.
- `label_keys`: eticheta cu și fără paranteza finală („Efect de diversificare (se scade)”).
- `load`: deschide registrul **de două ori** cu openpyxl, o dată cu formulele și o dată cu valorile salvate
  (`data_only`). Pentru fiecare foaie:
  - foaie ascunsă → `ignored` (așa e prinsă `Capital_vechi`);
  - titlu cu „nu se folosește” / „copie” → `ignored`;
  - antetul de coloane se caută în primele 30 de rânduri („31.12 an curent”, „31.12.2025”, …, din `run.toml`);
  - unitatea vine din antet („Valori în mii lei”, regex pe dicționarul din `run.toml`). Exact o unitate e
    acceptată; zero sau mai multe → `unit_problem`;
  - rânduri: eticheta = textele din stânga primei coloane de valori; **notele** = textele din dreapta (așa
    apare „în lucru, actuariat” din E11).
- `Sheet.value`: celulă goală / număr / text / formulă, fiecare cu explicația ei.
- `_formula`:
  - există valoarea salvată și formula se poate recalcula: le compară; diferența e conflict;
  - lipsește valoarea salvată: recalculează;
  - formula nu se poate recalcula: folosește valoarea salvată, cu notă.
- `_evaluate`: evaluator **sigur**, pe AST, fără `eval`. Acceptă doar + − × /, minus unar, constante,
  celule de pe aceeași foaie și `SUM(A1:B2)`. Adâncimea maximă e 20 (prinde referințele circulare), celula
  goală valorează 0, ca în Excel, iar împărțirea la zero e refuzată.

### `src/sfcr/locate.py`: catalog → exact o celulă
- `Fact`: id, descriere, `name` scurt, tip, stare, valoare (Decimal, lei sau fracție), sursă, motiv,
  probleme, note, verificări, foaie/celulă, `computed`, coloană.
- `_pick_sheets`: foaia preferată se recunoaște după nume **sau** după titlul din A1. Dacă nu e găsită, se
  caută în toate foile vizibile, cu o notă.
- `locate`, cazurile:
  - niciun rând → `missing`;
  - mai multe rânduri → `uncertain` (ambiguitatea nu e o alegere);
  - foaia nu are coloana cerută → `missing`;
  - celulă goală → `missing`; text → `uncertain`;
  - sumă de bani fără unitate → `uncertain`;
  - rată fără format procent → `uncertain` (nu se știe dacă 1,874 e fracție sau procent).
- Motivul arată, de exemplu: „eticheta «SCR» (rândul 10), foaia vizibilă «Capital» (găsită după numele foii),
  coloana C («31.12 an curent»), unitate «Valori în mii lei (Capital!A2)», valoare introdusă 148763.2 →
  148763200 lei”.

### `src/sfcr/money.py`: bani exacți și formatul raportului
- `to_decimal`: `Decimal(repr(float))`, adică valoarea **așa cum a fost tastată**, nu reprezentarea binară
  (0,1 rămâne 0,1).
- `_one_decimal`: `ROUND_HALF_UP`, o singură dată, pe valoarea nerotunjită; virgulă zecimală, punct la mii.
- `fmt_mil` („293,7 mil. lei”), `fmt_pct` („197,4 %”, cu spațiu), `fmt_count` („18.420”), `plain` (valoarea
  exactă, pentru tabele), `parse_ro_amount` („(15.000.000)” → 15000000).

### `src/sfcr/checks.py`: cifrele verificate între ele
- `compare_prior`, pentru fiecare figură din anul curent față de același catalog rulat pe registrul 2024:
  - valoare nenulă **identică** → `conflict` („probabil nu a fost actualizată”; așa e prinsă rata 1,874);
  - raport în afara intervalului [0,5; 2] → `uncertain` („posibilă eroare de unitate”).
  - Valoarea suspectă **nu** se repetă în mesaj, pentru că mesajul ajunge în draft.
- `run_checks`:
  - `sum`: termeni cu semn, `-abs:` pentru diversificare (semnul ei s-a schimbat între ani), termeni
    `optional` (nivelul 3 lipsește în 2024), `taint_total` (un nivel nesigur face și totalul nesigur);
  - gardă: dacă două figuri sunt găsite în aceeași celulă, verificarea nu dovedește nimic, deci nu rulează;
  - toleranța e 1 leu; la eșec, **toate** figurile implicate devin `conflict`, fără să se aleagă una;
  - `range`: coridorul MCR, 25–45 % din SCR.
- `derive`, pentru rată:
  - dacă intrările nu sunt utilizabile, sau SCR = 0, rata e gap;
  - dacă valoarea raportată lipsește sau nu se poate citi, se folosește calculul, cu notă;
  - dacă diferă de calcul cu mai mult de 0,0005, e `conflict`;
  - dacă raportata e ea însăși nesigură (de exemplu identică cu N-1), tot `conflict`.

### `src/sfcr/decisions.py`: deciziile oamenilor
- `apply`: o decizie se aplică **doar** dacă:
  - e pentru anul rulării (`meta.reporting_year`);
  - figura e în conflict sau nesigură;
  - **toate** valorile din `observed` sunt exact cele de acum.
- Altfel nu se aplică și conflictul se redeschide. Așa o decizie nu poate fi purtată în tăcere pe alt registru.
- `choice = "computed"` sau id-ul figurii alese. Rezultatul e starea `decided`, iar sursa include cine a decis și când.

### `src/sfcr/evidence.py`: afirmații din documente
- `Documents`: textul pe pagini (PDF prin pypdf, DOCX pe paragrafe prin python-docx, TXT direct); spațiile
  normalizate, NFC.
- `verify`, condițiile:
  - documentul există;
  - citatul apare **verbatim**;
  - `clause` (ce se inserează în text) face parte din citat;
  - pentru sume: citatul dă exact `value_lei`, și e **prima sumă după eticheta** „Dividende plătite” (altfel
    s-ar putea lua coloana 2024, cu 12.000.000);
  - coroborarea (PV AGA) conține aceeași sumă.
- `verify_all`: dovezile sunt legate de an; cererile respinse au și ele un citat care le contrazice
  (reasigurarea), verificat în document.
- `shared_ngrams`: secvențele comune de n cuvinte între draft și textul altei companii.

### `src/sfcr/compose.py`: textul
- Șablonul (`template_E.toml`) e textul E 2024 cu **sloturi**: `{scr}`, `{comparison.scr}`,
  `{evidence.dividends}`, `{clause.dividend-policy}`, `{coverage.mcr}`, `{year}`.
- `Context.slot` rezolvă fiecare slot; o figură care nu e utilizabilă devine `figure_gap`.
- `brief` și `reason_of(short=True)`: în draft apare motivul **scurt** (numele figurii, prima problemă,
  `claim`-ul dovezii), fără numele registrului și fără citatele lungi. Motivul complet merge în lista de
  probleme (regula 3).
- `_coverage`: „a fost acoperită integral” apare doar dacă MCR e utilizabil **și** nivelul 1 ≥ MCR (decizia ta).
- `render_text`: `whole_gap_on` transformă propoziția întreagă într-un singur gap (MCR, SCR), nu trei gap-uri
  înșirate.
- `sentence`, trei feluri de propoziții:
  - `fixed`: textul legal aprobat în config;
  - `variant`: nivelul 3 (0 → „nu a deținut”, > 0 → frază cu sumă, lipsă → gap);
  - `requires`: formula standard, doar dacă dovada e verificată.
- `resolve_comparison`:
  - valoarea N-1 vine din **cel puțin două surse care concordă**, dintre registrul 2024, coloana „an
    anterior” și textul raportului 2024;
  - direcția se calculează pe valori nerotunjite; sub 0,5 % decide omul;
  - cauza vine doar dintr-o dovadă cu `explains = "scr"` și `direction` egală cu direcția calculată, altfel
    e gap.
- `sentence_regex` / `published`: **același șablon, citit ca regex**, extrage cifrele din raportul de anul
  trecut. Folosește la back-test, la a treia sursă pentru SCR N-1 și, anul viitor, la citirea draftului 2025
  (există test). Un gap nu e niciodată citit ca cifră.

### `src/sfcr/backtest.py`
- `token_count`: numără un număr ca **token întreg** („12,4” nu e numărat în „412,4”).
- `validate_mapping`: fiecare intrare din `mapping_2024.toml` e citită din registrul 2024, cu unitatea foii,
  și comparată cu textul 2024. Dacă nu se potrivește, caută celula care dă textul (așa găsește C6 pentru
  „12,6”). Avertizează când căutarea pe subșir ar greși.
- `run`: rulează `analyse(2024)` și compară fiecare slot calculat cu cel publicat. Nivelul 3 e „așteptat”,
  nu „diferă”. Dacă lipsește un fișier, back-test-ul e sărit, cu motivul scris, și rularea nu se oprește.

### `src/sfcr/outputs.py`
- Toate fișierele sunt **deterministe**: fără timestamp, ordine fixă, LF. Două rulări dau octeți identici.
- `figures_csv`, `checks_csv`.
- `mapping_toml`: mappingul 2025 generat (id, text, apariție calculată pe token, celulă, unitate, motiv).
- `issues_md`: lista de probleme pentru echipa CFO-ului.
- `manifest`: sha256 pe intrări (cu `read_by_program`), pe config și pe ieșiri, plus versiunile de Python
  și de biblioteci.

### `config/` (tot ce se schimbă de la an la an)
- `run.toml`: anul, șabloanele de nume, foile de ignorat, antetele de coloane, dicționarul de unități,
  toleranțele (1 leu; rata 0,0005; mărimea între 0,5× și 2×; direcția de la 0,5 %), n-gram = 6.
- `catalogue.toml`: 15 figuri (`labels` cu aliasuri, foaia după nume/titlu, `kind`, `column`, `name`), rata
  derivată și 5 verificări declarative.
- `template_E.toml`: propozițiile E, sloturile, regula de comparație și regula de acoperire MCR.
- `decisions.toml` (în română, pentru că ajunge la echipa CFO-ului):
  - 4 politici;
  - 1 decizie (rata, cu `observed`);
  - 5 dovezi (cauza SCR, formula standard, MCR în curs, dividendele, politica de dividende);
  - 3 cereri respinse din email (cifra de anul trecut, reasigurarea, formulările Dunărea);
  - 1 text fix (temeiul legal).

### `tests/` (48)
- `conftest.py`: copiază `date/` într-un folder temporar; `run(change)` modifică **copia** registrului cu
  openpyxl. Atenție: salvarea cu openpyxl șterge valorile salvate ale formulelor, deci în teste totalurile
  sunt mereu recalculate.
- `test_broken_workbooks.py` (35): rânduri mutate, formulă fără valoare, unități (lei, lipsă, greșită, euro,
  milioane), foaia ascunsă făcută vizibilă și redenumită, copia veche deghizată în „Capital”, foaia redenumită
  sau reordonată, etichetă duplicată, variante de etichetă, MCR completat / neacoperit de nivelul 1 / în afara
  coridorului / copiat din 2024 / ca text, rata corectată / greșită altfel / ca formulă, SCR diferit între foi,
  număr ca text, total suprascris, nivel 2 lipsă, nivel 3 > 0, SCR în creștere, variație sub prag, antete cu
  anul, etichete în coloana A, diversificare negativă, gap-uri scurte.
- `test_decisions_evidence.py` (8): decizie pentru alt an, citat modificat, cauză cu altă direcție, suma
  dividendelor din coloana 2024, back-test-ul prinde erorile din mapping, determinismul, regulile textului,
  anul viitor citește draftul de anul acesta.
- `test_money.py` (5): half-up la ,x5; separatorul de mii; totalul ≠ suma rotunjitelor; o singură rotunjire;
  Decimal din float.

### `output/` (7 fișiere)
`raport_2025_sectiunea_E.txt`, `cifre_E_2025.csv`, `verificari_E_2025.csv`, `probleme_E_2025.md`,
`mapping_2025.toml`, `backtest_2024.md`, `manifest.json`.

---

## 5. Capcanele din materiale și cum le prinde codul

| ID | Capcana | Unde e prinsă |
|---|---|---|
| R1 | Capital, SCR_module, Provizioane și Daune au trecut la **mii lei**, Prime a rămas în lei | unitatea per foaie din antet (`workbook.load`); verificarea de ordin de mărime |
| R2 | rândurile s-au mutat (nivel 3 inserat): mappingul vechi ar citi celule greșite | căutare după etichetă (`locate`) |
| R3 | foaia ascunsă `Capital_vechi` cu cifrele 2024 | `sheet_state` + titlul „NU SE FOLOSEȘTE”; ambiguitatea, dacă e făcută vizibilă |
| R4 | totalul e formulă, poate fără valoare salvată | `_formula` / `_evaluate` |
| R5 | diversificarea și-a schimbat semnul | `-abs:scr_div` în verificare; mărimea comparată pe valoare absolută |
| V1 | MCR lipsește (momeală: 30 % × SCR = 44,6) | gap; nimic estimat; nota actuarială citată |
| V2 | rata 187,4 % = cea din 2024 | identic cu N-1 + calcul ≠ raportat → conflict → decizie legată de valori |
| P1 | mappingul 2024: „12,6” → C7 greșit | `validate_mapping` |
| P2 | „12,4” în „412,4” | `token_count` |
| T1 | SCR „în creștere … ca urmare a primelor” nu mai e adevărat | direcția calculată; cauza doar din dovadă |
| D5/D6 | CFO-ul cere „datorită noului program de reasigurare” | cerere respinsă, contrazisă de citat; termeni interziși verificați în text |
| D7 | „luați formulări de la Dunărea” | n-grame de 6 cuvinte |
| F1 | 262,4 + 31,2 = 293,6, dar totalul e 293,7 | totalul se ia din sursă |
| F4 | rotunjirea la ,x5 | Decimal ROUND_HALF_UP + test |

---

## 6. Decizii și de ce

| Decizie | Cine | De ce |
|---|---|---|
| ieșirea în `output/` din rădăcină, intrările din folderul curent | tu | zip-ul pune `output/` lângă `src/` |
| „MCR acoperită integral” doar dacă nivelul 1 ≥ MCR | tu | nivelul 2 contează la MCR doar până la o limită care nu e în registru; e o afirmație semnată de CFO |
| rata = calculul, legată de valorile văzute | propunere, „de confirmat de CFO” | C12 e copiată din 2024; pe alt registru decizia **nu** se aplică |
| nicio sursă nu câștigă implicit | politică | regula din temă: nicio alegere tăcută |
| un gap mai degrabă decât o estimare | politică | asimetrie de 100× între costul unei cifre greșite și al unui gap |
| `decisions.toml` în română | audit | ajunge în lista de probleme citită de echipa CFO-ului |
| gap-uri scurte în draft, detaliile în lista de probleme | tu (regula 3) | „short, concrete reason” |
| DESIGN.md în 4 pagini la interlinie 1,4 | tu | „at most 4 pages” e maximul la orice randare rezonabilă |
| `notes/` nu intră în zip; repo-ul public | tu | zip-ul conține ce cere tema; datele sunt fictive |

---

## 7. Ce se întâmplă pe registrul lor (testul ascuns)

- **Rata corectată** în C12: fără conflict și fără decizie; 197,4 % apare direct.
- **Rata tot greșită, dar alte cifre:** decizia nu se aplică (`observed` diferă), iar rata e gap cu ambele
  valori. **E intenționat** și e scris în README.
- **MCR completat:** apare cifra, coridorul 25–45 % e verificat, iar „acoperită integral” doar dacă nivelul 1
  ajunge. Plus o notă: nota actuarială spunea „în curs”, deci trebuie confirmat că valoarea e finală.
- **MCR = 45.570** (cea de anul trecut): identic cu N-1 → conflict → gap.
- **Rânduri mutate, foi redenumite sau reordonate, unitate schimbată, etichete cu altă scriere:** aceleași
  cifre.
- **Foaia veche făcută vizibilă:** ignorată după titlu; dacă și titlul e schimbat în „Capital”, etichetele
  ambigue devin gap.
- **Lipsă unitate / număr ca text / totaluri care nu se adună / SCR diferit între foi:** gap sau conflict,
  niciodată o cifră aleasă.
- **SCR în creștere:** „în creștere”, iar cauza (care explică o scădere) cade și devine gap.
- **Programul nu se oprește** decât dacă lipsește `registru_2025.xlsx` (exit 2).

---

## 8. Puncte slabe, spuse înainte să fie întrebate

- **Etichetele** sunt un dicționar întreținut de om (`labels`). O etichetă complet nouă dă un gap, nu o cifră
  greșită, dar dă un gap.
- **Identic cu N-1 = conflict** prinde și o valoare care chiar nu s-a schimbat (de exemplu un împrumut
  subordonat de nivel 2). Soluția e o decizie cu `choice = <figura>` și `observed`.
- **Intervalul 0,5×–2×** ar semnala o schimbare reală foarte mare (de exemplu o achiziție).
- **Formulele:** doar aritmetică simplă pe aceeași foaie; restul folosește valoarea salvată, cu notă.
- **Doar secțiunea E.** PV-ul CA scanat (fără strat de text, ar cere OCR) și emailul nu sunt citite de
  program; manifestul arată asta.
- **„copie” în `ignore_if_title_contains`** ar ignora o foaie legitimă care are „copie” în titlu (e raportat,
  deci vizibil).
- **Regula pentru MCR e conservatoare:** cu nivel 1 < MCR și nivel 2 eligibil suficient, scriem gap, deși
  fraza ar putea fi adevărată.

---

## 9. Întrebări probabile și răspunsul scurt

**De ce nu folosești mappingul 2024?** E ancorat pe coordonate și pe textul cifrei, deci se strică imediat
ce rândurile se mută sau cifrele se schimbă. Și e greșit („12,6”). Îl folosesc doar ca test pentru catalog, pe
anul lui.

**De ce `Decimal(repr(float))`?** openpyxl dă float. `repr` dă cea mai scurtă reprezentare care se întoarce
în același float, adică exact ce a tastat omul. `Decimal(float)` ar aduce zgomotul binar
(0,1000000000000000055…).

**De ce nu calculezi MCR (30 % din SCR, ca anul trecut)?** E o estimare nesusținută, iar regula temei spune că
un gap e mai bun decât o cifră greșită. Nota actuarială spune explicit că MCR vine separat.

**De ce leagă decizia de valori?** Dacă vine un registru corectat sau altul, decizia veche nu are voie să
rezolve tăcut un conflict nou. Omul vede din nou conflictul și decide pe datele noi.

**Unde ai folosi un LLM?** Pentru a propune: pasaje candidate în scanuri, potrivirea etichetelor noi cu cele
vechi, reformulări cu cifrele puse de cod după aceea. Niciodată pentru a produce sau alege o cifră, a rezolva
un conflict sau a scrie o cauză fără citat. Exemplul care ar strânge regula: un model care scapă „în
principal” sau adaugă „și programul de reasigurare” pentru că emailul CFO-ului era în context.

**Cum știi că „a scăzut” e adevărat?** Nu copiez niciodată cuvântul. Calculez direcția pe valori
nerotunjite, față de valoarea N-1 confirmată de cel puțin două surse; sub 0,5 % decide omul; cauza doar dintr-un
citat verbatim care explică exact direcția calculată.

**De ce evaluator pe AST și nu `eval`?** Formula vine dintr-un fișier al clientului. `eval` ar executa cod.
AST-ul acceptă doar operațiile permise.

**Cum ar scala la 25 de clienți?** Motorul, verificările, formatul și modelul de decizii rămân la fel. Se
schimbă etichetele, șabloanele și sursele. Strangularea e onboarding-ul și revizuirea de expert, toate în
februarie–aprilie. Ancorarea pe șabloanele standard (S.23.01, S.25.01, S.28.01) reduce munca per client.

**Ce ai face cu încă 4 săptămâni?** Secțiunile A–D (aceeași mașinărie: prime, daune, investiții, provizioane),
OCR cu verificare umană pentru scanuri, diff propoziție cu propoziție față de anul trecut, rulare în paralel
cu echipa CFO-ului.

**Cum ai lucrat cu AI-ul?** Vezi `ai/AI.md`:
- respins: „4 pagini la interlinie 1,25 ajung” și „`notes/` în zip”;
- prins: comanda `python` care nu exista pe macOS, apoi „40 ways” fals, găsit la audit;
- păstrat pentru mine: regula pentru MCR;
- niciodată singur: modificarea `decisions.toml`.

---

## 10. Istoric

1. **Sesiunea 1:** auditul capcanelor (`notes/AUDIT_CAPCANE.md`), deciziile pentru fonduri proprii și SCR,
   DESIGN.md, planul de implementare (fără cod).
2. **Sesiunea 2:** codul, configul, testele; venv-ul (pe macOS nu există `python`); jurnalul
   `notes/IMPLEMENTARE.md` cu 11 bug-uri reparate și deviațiile de la plan.
3. **Sesiunea 3:**
   - auditul complet față de temă;
   - `decisions.toml` tradus;
   - nivelul 3 „așteptat” în back-test;
   - 8 teste noi;
   - README-ul;
   - DESIGN.md: afirmațiile corectate, de la 2.348 la 1.897 de cuvinte, 4 pagini;
   - gap-uri scurte;
   - git și GitHub;
   - `ai/AI.md`.

**Final:**
- conversațiile brute (JSONL, needitate) sunt în `ai/conversations/`, doar în zip; în repo-ul public nu sunt,
  pentru că conțin adresa ta de email;
- zip-ul `andrei_neagoe.zip` conține `README.md`, `DESIGN.md`, `ai/`, `config/`, `output/`, `src/`, `tests/`,
  `requirements.txt` și `.git/` (istoricul cerut de temă);
- ultimul pas manual: `/export` al sesiunii 3, adăugat în zip, apoi încărcarea pe Drive.

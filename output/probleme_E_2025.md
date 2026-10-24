# Probleme: secțiunea E, 2025

- **1** locuri de completat în text înainte de publicare
- **1** figuri rezolvate prin decizie, **2** figuri care nu sunt ok
- **2** verificări eșuate din 36

## Locuri de completat în text

- **cerința de capital minim (MCR) și acoperirea ei**: Cerința de capital minim (MCR): celula Capital!C11 este goală; pe rând scrie «în lucru, actuariat» (Capital!E11); nota_functia_actuariala_2026-02-02.docx (paragraful 4): „Calculul cerinței de capital minim este în curs de finalizare și va fi transmis separat.”; «a fost acoperită integral» nu se poate afirma fără MCR

## Figuri care nu sunt ok

- **mcr** (lipsă), Cerința de capital minim (MCR): celula Capital!C11 este goală; pe rând scrie «în lucru, actuariat» (Capital!E11)
- **solvency_ratio_reported** (conflict), Rata de solvabilitate, așa cum e introdusă în registru: registru_2025.xlsx!Capital!C12 = 1.874 este identică cu valoarea din registru_2024.xlsx (registru_2024.xlsx!Capital!C11); probabil nu a fost actualizată

## Decizii din config/decisions.toml

- **solvency-ratio-2025** (solvency_ratio): aplicată: valorile observate sunt identice (solvency_ratio_reported = 1.874, own_funds_total = 293699300, scr = 148763200)
  - solvency_ratio: problema inițială: raportat 187,4 % (registru_2025.xlsx!Capital!C12), calculat 197,4 % (registru_2025.xlsx!Capital!C8 / registru_2025.xlsx!Capital!C10): valorile diferă

## Verificări eșuate sau care nu au putut rula

- **diferit-de-N-1:solvency_ratio_reported** (eșuat): registru_2025.xlsx!Capital!C12 = 1.874 este identică cu valoarea din registru_2024.xlsx (registru_2024.xlsx!Capital!C11); probabil nu a fost actualizată
- **mcr-coridor** (nu s-a putut rula): mcr: celula Capital!C11 este goală; pe rând scrie «în lucru, actuariat» (Capital!E11)
- **calcul:solvency_ratio** (eșuat): raportat 187,4 % (registru_2025.xlsx!Capital!C12), calculat 197,4 % (registru_2025.xlsx!Capital!C8 / registru_2025.xlsx!Capital!C10)

## Foi ignorate

- registru_2025.xlsx, foaia «Capital_vechi»: foaie ascunsă (titlu «NU SE FOLOSEȘTE (copie 2024)»)

## Unitatea fiecărei foi

| Foaie | registru_2025.xlsx | registru_2024.xlsx |
|---|---|---|
| Prime | Valori în lei (Prime!A2) | Valori în lei (Prime!A2) |
| Daune | Valori în mii lei, cu excepția numărului de dosare (Daune!A2) (schimbată) | Valori în lei (Daune!A2) |
| Investitii | Valori în lei (Investitii!A2) | Valori în lei (Investitii!A2) |
| Provizioane | Valori în mii lei (Provizioane!A2) (schimbată) | Valori în lei (Provizioane!A2) |
| SCR_module | Valori în mii lei (SCR_module!A2) (schimbată) | Valori în lei (SCR_module!A2) |
| Capital | Valori în mii lei (Capital!A2) (schimbată) | Valori în lei (Capital!A2) |

## Dovezi din documente

- **scr-change-cause** (verificată): SCR a scăzut în 2025, în principal din cauza scăderii riscului de piață. găsit cuvânt cu cuvânt: nota_functia_actuariala_2026-02-02.docx (paragraful 1). Motiv: Nota funcției actuariale este singurul document al Societății care explică variația SCR; registrul o confirmă (riscul de piață scade de la 58,3 la 41,9 mil. lei).
- **standard-formula** (verificată): SCR se calculează cu formula standard, fără parametri specifici proprii. găsit cuvânt cu cuvânt: nota_functia_actuariala_2026-02-02.docx (paragraful 5). Motiv: Confirmă pentru 2025 fraza din raportul 2024 despre metoda de calcul.
- **mcr-pending** (verificată): Calculul MCR nu era finalizat la data notei. găsit cuvânt cu cuvânt: nota_functia_actuariala_2026-02-02.docx (paragraful 4). Motiv: Explică de ce registrul nu are MCR; se citează în motivul locului de completat.
- **dividends-paid-2025** (verificată): În 2025 s-au plătit dividende de 15.000.000 lei. găsit cuvânt cu cuvânt: situatii_financiare_2025_extras.pdf, p. 1 (Indicatori selectați); confirmat de proces_verbal_AGA_2025-04-24.txt (punctul 3). Motiv: Cifră contabilă: sursa este situațiile financiare auditate (emailul directorului financiar, punctul 5), confirmată de hotărârea AGA.
- **dividend-policy** (verificată): Politica de dividende aprobată de Consiliul de Administrație rămâne neschimbată. găsit cuvânt cu cuvânt: proces_verbal_AGA_2025-04-24.txt (punctul 4). Motiv: Susține clauza «conform politicii de dividende aprobate de Consiliul de Administrație» pentru 2025.

## Text fix aprobat (fără sursă în documentele anului)

- **own-funds-legal-basis** (aprobat de Andrei Neagoe (propunere), de confirmat de funcția de conformitate; sursa textului: raport_2024.txt, secțiunea E.1, paragraful 2): Temeiul legal al clasificării; neschimbat în 2025 și fără cifre. De reconfirmat anual de funcția de conformitate.

## Cereri neacceptate

- **Unde lipsește o cifră, se pune cea de anul trecut.** (cerut în email_director_financiar.txt, punctul 2): Regula 1 a raportului. Anul acesta lipsește MCR; cifra de anul trecut, 45,6 mil. lei, ar fi o cifră greșită prezentată ca fiind curentă. Textul arată în schimb un loc de completat (politica no-prior-year-substitution).
- **Rata de solvabilitate s-a îmbunătățit datorită noului program de reasigurare.** (cerut în email_director_financiar.txt, punctul 3): Funcția actuarială a Societății arată că programul a fost reînnoit în aceleași condiții, fără efect asupra SCR. Contrazis de: găsit cuvânt cu cuvânt: nota_functia_actuariala_2026-02-02.docx (paragraful 3).
- **Se preiau formulări din raportul Asigurări Dunărea.** (cerut în email_director_financiar.txt, punctul 4): Regula 4 a raportului: nu se refolosesc niciodată formulările altei companii.

## Reguli aplicate

- **no-prior-year-substitution**: O cifră lipsă din anul curent nu se înlocuiește niciodată cu cea de anul trecut. Devine un loc de completat vizibil. (README §4 regula 1; email_director_financiar.txt punctul 2)
- **no-silent-precedence**: Când două surse dau valori diferite pentru aceeași cifră, niciuna nu câștigă implicit. Cifra rămâne în conflict până o rezolvă o decizie de mai jos. (README §5 livrabilul 2)
- **hidden-sheets-are-not-sources**: Foile ascunse sunt citite doar ca să se raporteze că au fost ignorate. (registru_2025.xlsx, foaia Capital_vechi, A1)
- **explanations-need-evidence**: O frază care afirmă o direcție sau o cauză apare doar dacă se sprijină pe o comparație calculată (direcția) sau pe o dovadă aprobată mai jos (cauza). (README §4 regula 2)

## Observații

- solvency_ratio: conflict rezolvat prin decizia «solvency-ratio-2025»: Rata introdusă în registru (187,4 %) este identică cu cea din 2024, în timp ce aceeași foaie dă fonduri proprii eligibile de 293.699,3 mii lei și un SCR de 148.763,2 mii lei, adică 197,4 %. Rata este, prin definiție, fondurile proprii eligibile împărțite la SCR, iar ambele intrări trec propriile verificări (nivelurile se adună la total; SCR este același cu cel din foaia SCR_module). Celula introdusă este deci considerată neactualizată din 2024 și se folosește valoarea calculată, rotunjită o singură dată din câtul nerotunjit.

## Back-test pe 2024

- secțiunea E 2024: 10 sloturi reproduse, 1 cu diferență așteptată, 0 diferite (detalii în backtest_2024.md)
- mapping 2024, «12,6» → Investitii!C7: **greșit**: celula Investitii!C7 («Pondere titluri de stat») dă «0,0», nu «12,6»; celula care dă «12,6»: Investitii!C6 «Venituri din investiții»
- mapping 2024, «12,4» → SCR_module!C10: «12,4» apare de 3 ori ca subșir, dar de 1 ori ca număr întreg; o căutare pe subșir ar nimeri în interiorul altui număr

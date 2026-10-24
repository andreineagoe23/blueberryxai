"""Section E of the SFCR, rolled forward.

Run from the folder holding the client's files:

    cd date && python ../src/main.py

Reads the inputs from the current folder and config/ next to src/, writes everything to output/
next to src/.
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sfcr import backtest  # noqa: E402
from sfcr.outputs import write_all  # noqa: E402
from sfcr.pipeline import InputError, analyse, load_config  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Secțiunea E a SFCR, din registrul anului și documentele societății.")
    p.add_argument("--input", type=Path, default=Path.cwd(), help="folderul cu fișierele clientului (implicit: cel curent)")
    p.add_argument("--config", type=Path, default=ROOT / "config", help="folderul cu config (implicit: config/)")
    p.add_argument("--out", type=Path, default=ROOT / "output", help="folderul de ieșire (implicit: output/)")
    args = p.parse_args(argv)

    cfg = load_config(args.config)
    year = cfg["run"]["reporting_year"]
    try:
        a = analyse(year, args.input, cfg)
        bt_md, bt_summary = backtest.run(cfg, args.input)
    except InputError as e:
        print(f"Eroare: {e}", file=sys.stderr)
        return 2
    written = write_all(a, cfg, args.input, args.config, args.out, bt_md, bt_summary)

    print(f"Secțiunea E {year}: {len(a.draft.gaps)} locuri de completat, "
          f"{sum(f.status == 'decided' for f in a.facts.values())} figuri decise prin config, "
          f"{sum(r.result == 'eșuat' for r in a.results)} verificări eșuate.")
    for name in written:
        print(f"  {args.out / name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

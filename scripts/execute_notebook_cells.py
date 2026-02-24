#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def run_notebook(path: Path) -> None:
    nb = json.loads(path.read_text(encoding="utf-8"))
    env = {"__name__": "__main__"}
    code_cells = [c for c in nb.get("cells", []) if c.get("cell_type") == "code"]

    print(f"Executing {path.name} ({len(code_cells)} code cells)")
    for idx, cell in enumerate(code_cells):
        src = "".join(cell.get("source", []))
        try:
            exec(compile(src, f"{path.name}#cell{idx}", "exec"), env, env)
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"FAILED {path.name} cell {idx}: {type(exc).__name__}: {exc}") from exc
    print(f"OK {path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute code cells from .ipynb files without nbconvert.")
    parser.add_argument("notebooks", nargs="+", help="Notebook paths")
    args = parser.parse_args()

    for nb_path in args.notebooks:
        run_notebook(Path(nb_path))

    print("All notebook code cells executed successfully.")


if __name__ == "__main__":
    main()

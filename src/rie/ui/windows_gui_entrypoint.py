from __future__ import annotations

import os
from pathlib import Path


_SMOKE_ENV = "RCIS_PACKAGING_SMOKE_TEST"
_SMOKE_MARKER_PATH_ENV = "RCIS_PACKAGING_SMOKE_MARKER_PATH"
_SMOKE_MARKER = "RCIS_PACKAGING_SMOKE_OK"


def main() -> None:
    if os.environ.get(_SMOKE_ENV) == "1":
        import tkinter  # noqa: F401
        import pypdf  # noqa: F401
        from rie.ui.tkinter_grounded_prompt_app import GroundedPromptTkApplication  # noqa: F401

        marker_path = os.environ.get(_SMOKE_MARKER_PATH_ENV, "").strip()
        if not marker_path:
            raise RuntimeError(
                "RCIS_PACKAGING_SMOKE_MARKER_PATH must be set in packaging smoke mode"
            )
        Path(marker_path).write_text(_SMOKE_MARKER + "\n", encoding="ascii")
        return

    from rie.ui.tkinter_grounded_prompt_app import main as tkinter_main

    tkinter_main()


if __name__ == "__main__":
    main()

from __future__ import annotations

import re


def slugify(value: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return base or "item"

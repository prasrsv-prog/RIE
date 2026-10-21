"""Presentation-only, two-locale interface translation foundation (C20-H1).

Never translate product identities, operator-authored briefs, rights evidence,
internal codes or grounded prompt payloads through this facade.
"""
from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import re
from string import Formatter
from typing import Mapping

DEFAULT_LOCALE = "id-ID"
SUPPORTED_LOCALES = ("id-ID", "en-US")
CATALOG_SCHEMA_VERSION = 1
_SIMPLE_FIELD = re.compile(r"[A-Za-z_][A-Za-z_0-9]*\Z")


class LocalizationError(ValueError):
    """Catalog is missing, inconsistent, or contains unsafe formatting."""


def resolve_locale(locale: object) -> str:
    """Fall back to Indonesian only for unrecognized stored preferences."""
    return locale if isinstance(locale, str) and locale in SUPPORTED_LOCALES else DEFAULT_LOCALE


def _fields(text: str) -> frozenset[str]:
    fields = set()
    try:
        for _, name, spec, conversion in Formatter().parse(text):
            if name is None:
                continue
            if not _SIMPLE_FIELD.fullmatch(name) or spec or conversion:
                raise LocalizationError("complex or unsafe translation placeholder")
            fields.add(name)
    except LocalizationError:
        raise
    except ValueError as exc:
        raise LocalizationError("invalid translation template braces") from exc
    return frozenset(fields)


def load_catalogs(directory: Path | None = None) -> dict[str, dict[str, str]]:
    """Read and validate BOTH locale catalogs; no network or user data access."""
    root = Path(__file__).with_name("locales") if directory is None else Path(directory)
    catalogs = {}
    for locale in SUPPORTED_LOCALES:
        path = root / (locale + ".json")
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise LocalizationError("locale catalog missing or corrupt: " + locale) from exc
        if (not isinstance(document, dict)
                or set(document) != {"schema_version", "locale", "messages"}
                or document["schema_version"] != CATALOG_SCHEMA_VERSION
                or document["locale"] != locale
                or not isinstance(document["messages"], dict)
                or not document["messages"]):
            raise LocalizationError("invalid locale catalog schema: " + locale)
        messages = document["messages"]
        if any(not isinstance(k, str) or not k.strip()
               or not isinstance(v, str) or not v.strip()
               for k, v in messages.items()):
            raise LocalizationError("empty key or translation: " + locale)
        catalogs[locale] = messages
    a, b = (catalogs[locale] for locale in SUPPORTED_LOCALES)
    if a.keys() != b.keys():
        raise LocalizationError("locale catalogs have different keys")
    for key in a:
        if _fields(a[key]) != _fields(b[key]):
            raise LocalizationError("locale placeholder mismatch for " + key)
    return catalogs


@lru_cache(maxsize=1)
def _default_catalogs() -> dict[str, dict[str, str]]:
    return load_catalogs()


class Localizer:
    """Mutable locale selection; never modifies application/model state."""

    def __init__(self, locale: str = DEFAULT_LOCALE,
                 *, catalogs: Mapping[str, Mapping[str, str]] | None = None) -> None:
        if locale not in SUPPORTED_LOCALES:
            raise ValueError("unsupported UI locale")
        self._catalogs = catalogs if catalogs is not None else _default_catalogs()
        self._locale = locale

    @property
    def locale(self) -> str:
        return self._locale

    def set_locale(self, locale: str) -> None:
        if locale not in SUPPORTED_LOCALES:
            raise ValueError("unsupported UI locale")
        self._locale = locale

    def tr(self, key: str, **values: object) -> str:
        # Fail on unknown keys: a missing rights/safety text must not be hidden.
        template = self._catalogs[self._locale][key]
        required = _fields(template)
        if set(values) != set(required):
            raise ValueError("translation placeholder arguments mismatch for " + key)
        return template.format_map(values)

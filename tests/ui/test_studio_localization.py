"""Offline tests of C20-H1 presentation localization only."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from rie.ui.studio_localization import (
    DEFAULT_LOCALE, SUPPORTED_LOCALES, Localizer, LocalizationError,
    load_catalogs, resolve_locale,
)
from rie.ui.studio_ui_preferences import (
    default_ui_preferences_path, load_preferred_locale, save_preferred_locale,
)


def test_only_indonesian_and_english_enabled():
    assert SUPPORTED_LOCALES == ("id-ID", "en-US")
    assert DEFAULT_LOCALE == "id-ID"


def test_catalog_exact_parity_and_meaningful_coverage():
    catalogs = load_catalogs()
    assert len(catalogs["id-ID"]) == len(catalogs["en-US"]) >= 68
    assert all(catalogs["id-ID"][k] and catalogs["en-US"][k]
               for k in catalogs["id-ID"])
    assert catalogs["en-US"]["nav.create"] != catalogs["id-ID"]["nav.create"]


def test_translations_and_placeholders():
    l = Localizer()
    assert l.tr("nav.create") == "Buat Visual"
    assert l.tr("nav.more", count=6) == "Lainnya (6)"
    l.set_locale("en-US")
    assert l.tr("nav.create") == "Create Visual"
    assert l.tr("nav.more", count=6) == "More (6)"


def test_live_localizer_switch_retains_independent_data():
    creative_brief = {"product_id": "ffs21", "variant_id": "Hustle",
                      "prompt": "PRODUCT LOCKS: Keep original."}
    original = dict(creative_brief)
    l = Localizer()
    l.set_locale("en-US")
    l.set_locale("id-ID")
    assert creative_brief == original


def test_unknown_keys_fail_closed():
    with pytest.raises(KeyError):
        Localizer().tr("not.defined")


def test_missing_or_extra_format_argument_fails_closed():
    with pytest.raises(ValueError):
        Localizer().tr("nav.more")
    with pytest.raises(ValueError):
        Localizer().tr("nav.create", count=1)


def test_locale_validation_and_stored_preference_fallback():
    assert resolve_locale("pt-BR") == "id-ID"
    assert resolve_locale(None) == "id-ID"
    assert resolve_locale("en-US") == "en-US"
    with pytest.raises(ValueError):
        Localizer("fr-FR")
    l = Localizer()
    with pytest.raises(ValueError):
        l.set_locale("fr-FR")
    assert l.locale == "id-ID"


def test_catalog_rejects_missing_key(tmp_path):
    catalogs = load_catalogs()
    for locale in SUPPORTED_LOCALES:
        data = dict(catalogs[locale])
        if locale == "en-US":
            del data["nav.create"]
        (tmp_path / (locale + ".json")).write_text(json.dumps(
            {"schema_version": 1, "locale": locale, "messages": data}), encoding="utf-8")
    with pytest.raises(LocalizationError, match="different keys"):
        load_catalogs(tmp_path)


def test_catalog_rejects_placeholder_mismatch(tmp_path):
    catalogs = load_catalogs()
    for locale in SUPPORTED_LOCALES:
        data = dict(catalogs[locale])
        if locale == "en-US":
            data["nav.more"] = "More ({wrong})"
        (tmp_path / (locale + ".json")).write_text(json.dumps(
            {"schema_version": 1, "locale": locale, "messages": data}), encoding="utf-8")
    with pytest.raises(LocalizationError, match="placeholder mismatch"):
        load_catalogs(tmp_path)


def test_catalog_rejects_unsafe_format(tmp_path):
    catalogs = load_catalogs()
    for locale in SUPPORTED_LOCALES:
        data = dict(catalogs[locale])
        if locale == "en-US":
            data["nav.more"] = "More ({count.__class__})"
        (tmp_path / (locale + ".json")).write_text(json.dumps(
            {"schema_version": 1, "locale": locale, "messages": data}), encoding="utf-8")
    with pytest.raises(LocalizationError, match="unsafe"):
        load_catalogs(tmp_path)


def test_missing_or_corrupted_preference_defaults_to_indonesian(tmp_path):
    path = tmp_path / "studio-ui.json"
    assert load_preferred_locale(preferences_path=path) == "id-ID"
    path.write_text("{invalid", encoding="utf-8")
    assert load_preferred_locale(preferences_path=path) == "id-ID"
    path.write_text(json.dumps({"schema_version": 1, "locale": "fr-FR"}), encoding="utf-8")
    assert load_preferred_locale(preferences_path=path) == "id-ID"
    path.write_text(json.dumps({"schema_version": 1, "locale": "en-US", "other": 1}), encoding="utf-8")
    assert load_preferred_locale(preferences_path=path) == "id-ID"


def test_save_and_load_preference_roundtrip(tmp_path):
    path = tmp_path / "studio-ui.json"
    assert save_preferred_locale("en-US", preferences_path=path) == path
    assert load_preferred_locale(preferences_path=path) == "en-US"
    assert set(json.loads(path.read_text())) == {"schema_version", "locale"}
    save_preferred_locale("id-ID", preferences_path=path)
    assert load_preferred_locale(preferences_path=path) == "id-ID"


def test_reject_unsupported_preference_without_writing(tmp_path):
    path = tmp_path / "studio-ui.json"
    with pytest.raises(ValueError):
        save_preferred_locale("fr-FR", preferences_path=path)
    assert not path.exists()


def test_preferences_location_is_isolated(tmp_path):
    env = {"LOCALAPPDATA": str(tmp_path / "Local")}
    assert default_ui_preferences_path(environ=env) == tmp_path / "Local" / "RCIS" / "studio-ui.json"


def test_legacy_intake_root_setting_never_mutated(tmp_path):
    old = tmp_path / "settings.json"
    raw = b'{"schema_version":1,"intake_root":"D:/old-frozen"}\n'
    old.write_bytes(raw)
    save_preferred_locale("en-US", preferences_path=tmp_path / "studio-ui.json")
    assert old.read_bytes() == raw

def test_c20_h3b_catalog_extends_parity_for_four_workspaces() -> None:
    catalogs = load_catalogs()
    assert len(catalogs['id-ID']) == len(catalogs['en-US'])
    assert len(catalogs['id-ID']) >= 120
    for key in (
        'workspace.products_title', 'workspace.assets_title',
        'workspace.approvals_title', 'workspace.workflow_title',
        'workspace.reason_codes', 'workspace.approved_references',
        'workspace.manual_handoff_declared',
    ):
        assert key in catalogs['id-ID'] and key in catalogs['en-US']
        assert catalogs['id-ID'][key] != catalogs['en-US'][key]

def test_c20_h3c_dynamic_status_catalog_parity() -> None:
    catalogs = load_catalogs()
    keys = (
        "status.prompt_ready", "status.prompt_failed", "status.brief_required",
        "status.prompt_empty", "status.prompt_review",
    )
    assert len(catalogs["id-ID"]) == len(catalogs["en-US"]) >= 128
    for key in keys:
        assert key in catalogs["id-ID"]
        assert key in catalogs["en-US"]
        assert catalogs["id-ID"][key] != catalogs["en-US"][key]


def test_c20_h3d_operational_status_catalog_parity() -> None:
    catalogs = load_catalogs()
    keys = (
        "status.products_unavailable", "status.products_connected",
        "status.assets_unavailable", "status.assets_connected",
        "status.assets_variant_needed", "status.search_select_product",
        "status.search_empty",
    )
    assert len(catalogs["id-ID"]) == len(catalogs["en-US"]) >= 151
    for key in keys:
        assert key in catalogs["id-ID"] and key in catalogs["en-US"]
        assert catalogs["id-ID"][key] != catalogs["en-US"][key]


def test_c20_i6_history_catalog_parity_and_existing_copy_reuse() -> None:
    catalogs = load_catalogs()
    id_messages = catalogs["id-ID"]
    en_messages = catalogs["en-US"]
    assert len(id_messages) == len(en_messages) == 151
    for key in (
        "history.title", "history.intro", "history.refresh", "history.empty",
        "history.count", "history.legacy_note", "history.details",
        "history.preview_placeholder",
    ):
        assert id_messages[key] != en_messages[key]
    assert id_messages["prompt.copy"] == "Salin Prompt"
    assert en_messages["prompt.copy_success"] == "Prompt copied."
    assert Localizer("id-ID").tr("history.count", count=2).startswith("2 " )
    assert Localizer("en-US").tr("history.count", count=2).startswith("2 " )


def test_c20_i9_presets_catalog_reuses_existing_workspace_without_persistence() -> None:
    catalogs = load_catalogs()
    id_messages = catalogs["id-ID"]
    en_messages = catalogs["en-US"]
    assert len(id_messages) == len(en_messages) == 151
    for key in (
        "presets.title", "presets.intro", "presets.legacy_note", "presets.refresh",
        "presets.empty", "presets.count", "presets.selection_hint", "presets.details",
    ):
        assert id_messages[key] != en_messages[key]
    assert Localizer("id-ID").tr("presets.count",count=1).startswith("1 ")
    assert Localizer("en-US").tr("presets.count",count=1).startswith("1 ")
    assert "History" == Localizer("en-US").tr("nav.history")

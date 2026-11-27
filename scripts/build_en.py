#!/usr/bin/env python3
"""Render the English page (en/index.html) from the Turkish source.

index.html is authored in Turkish and marks translatable content with
data-i18n="key" (element text) and data-i18n-attr="attr:key; ..." (attributes).
This script substitutes the strings from js/locales/en.js so the English page
ships fully translated markup that search engines can index.

The build is strict: an unknown key, a data-i18n element that is not plain
text, or an attribute that cannot be found aborts with a non-zero exit.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "index.html"
LOCALE = ROOT / "js" / "locales" / "en.js"
OUTPUT = ROOT / "en" / "index.html"

LANG = "en"
NOTICE = "<!-- Generated from index.html by scripts/build_en.py. Do not edit. -->"

ENTRY = re.compile(r"'([\w.]+)':\s*'((?:[^'\\]|\\.)*)'")
KEY_LINE = re.compile(r"^\s*'[\w.]+':", re.MULTILINE)
TEXT_BINDING = re.compile(
    r'(?P<open><(?P<tag>\w+)\b[^>]*?\sdata-i18n="(?P<key>[^"]+)"[^>]*>)(?P<text>[^<]*)(?P<close></(?P=tag)>)'
)
ATTR_BINDING_TAG = re.compile(r'<[^>]*?\sdata-i18n-attr="(?P<spec>[^"]+)"[^>]*>')
LANG_LINK = re.compile(r'<a\b[^>]*\sdata-lang="(?P<lang>\w+)"[^>]*>')


class BuildError(Exception):
    pass


def load_dictionary(path: Path) -> dict[str, str]:
    source = path.read_text(encoding="utf-8")
    entries = {key: re.sub(r"\\(.)", r"\1", value) for key, value in ENTRY.findall(source)}
    declared = len(KEY_LINE.findall(source))
    if len(entries) != declared:
        raise BuildError(f"{path.name}: parsed {len(entries)} of {declared} entries; check quoting")
    return entries


def lookup(dictionary: dict[str, str], key: str) -> str:
    try:
        return dictionary[key]
    except KeyError:
        raise BuildError(f'missing English translation for "{key}"') from None


def translate_text(markup: str, dictionary: dict[str, str]) -> str:
    expected = markup.count(' data-i18n="')

    def replace(match: re.Match[str]) -> str:
        value = html.escape(lookup(dictionary, match["key"]), quote=False)
        return f'{match["open"]}{value}{match["close"]}'

    markup, count = TEXT_BINDING.subn(replace, markup)
    if count != expected:
        raise BuildError(f"translated {count} of {expected} data-i18n elements; bindings must wrap plain text")
    return markup


def translate_attributes(markup: str, dictionary: dict[str, str]) -> str:
    def replace_tag(match: re.Match[str]) -> str:
        tag = match.group(0)
        for pair in match["spec"].split(";"):
            attr, key = (part.strip() for part in pair.split(":", 1))
            value = html.escape(lookup(dictionary, key), quote=True)
            tag, count = re.subn(rf'(\s{re.escape(attr)}=")[^"]*(")', rf"\g<1>{value}\g<2>", tag)
            if count != 1:
                raise BuildError(f'expected one "{attr}" attribute for "{key}", found {count}')
        return tag

    return ATTR_BINDING_TAG.sub(replace_tag, markup)


def mark_current_language(markup: str) -> str:
    def replace(match: re.Match[str]) -> str:
        link = match.group(0).replace(' aria-current="page"', "")
        if match["lang"] == LANG:
            link = link[:-1] + ' aria-current="page">'
        return link

    markup, count = LANG_LINK.subn(replace, markup)
    if count == 0:
        raise BuildError("no language links found")
    return markup


def set_document_language(markup: str) -> str:
    markup, count = re.subn(r'<html lang="[^"]*">', f'<html lang="{LANG}">\n{NOTICE}', markup, count=1)
    if count != 1:
        raise BuildError("<html lang> not found")
    return markup


def build() -> None:
    dictionary = load_dictionary(LOCALE)
    markup = SOURCE.read_text(encoding="utf-8")
    for step in (set_document_language, mark_current_language):
        markup = step(markup)
    markup = translate_text(markup, dictionary)
    markup = translate_attributes(markup, dictionary)

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(markup, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    try:
        build()
    except BuildError as error:
        sys.exit(f"build_en: {error}")

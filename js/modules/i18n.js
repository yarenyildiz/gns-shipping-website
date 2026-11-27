import en from '../locales/en.js';
import tr from '../locales/tr.js';

/**
 * Each language is a separate page. index.html is authored in Turkish and
 * scripts/build_en.py renders /en/ from it using js/locales/en.js, so crawlers
 * and visitors get the translated markup directly.
 *
 * At runtime the page language comes from <html lang>. This module only serves
 * strings that exist in JavaScript alone (form feedback, menu labels) and keeps
 * the language links pointing at the section the visitor is reading.
 */

const DEFAULT_LANG = 'tr';
const LEGACY_QUERY_PARAM = 'lang';
const dictionaries = { tr, en };

function pageLanguage() {
  const lang = document.documentElement.lang;
  return Object.hasOwn(dictionaries, lang) ? lang : DEFAULT_LANG;
}

/** Translate a runtime-only string into the page language. */
export function t(key) {
  return dictionaries[pageLanguage()][key] ?? dictionaries[DEFAULT_LANG][key] ?? key;
}

export function initI18n(root = document) {
  // Links shared before /en/ existed point at the Turkish page with ?lang=en.
  const requested = new URLSearchParams(window.location.search).get(LEGACY_QUERY_PARAM);
  if (requested === 'en' && pageLanguage() !== 'en') {
    window.location.replace(`/en/${window.location.hash}`);
    return;
  }

  root.querySelectorAll('[data-lang]').forEach((link) => {
    link.addEventListener('click', () => {
      link.hash = window.location.hash;
    });
  });
}

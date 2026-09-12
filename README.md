# Little Roundtable website

Product landing page, support, privacy policy and terms.

Site: https://wklken.me/roundtable-ai-site/

## Editing and publishing

- Homepage source: `landing.html`, `landing.css`, `landing.js`.
- Shared palette and language controls: `site.css`, `language.js`.
- Support/legal source: `generate.py`.
- English text registry: `locales/en.json`; translations: `locales/{language}.txt` (`stable-index|translation`, one entry per line). Preserve existing indices when adding copy. Update the English registry and all six translations together when changing text. The build rejects missing, duplicate and unknown strings.
- `localize.py` renders English, Simplified Chinese, Japanese, Korean, German, French and Spanish, with localized navigation, metadata and accessibility labels. English keeps the existing root URLs; other languages use `/{language}/`.

Run `python3 generate.py`, `python3 validate_site.py`, `node --check language.js` and `node --check landing.js`. Commit sources and generated `docs/` files. GitHub Pages publishes `main` → `/docs`. No app code or credentials belong here.

Language selection preserves the current page and anchor. The unqualified homepage remembers a previously chosen language when browser storage is available. Explicit localized links and direct legal-page links keep their own language. Without JavaScript, all localized pages and fallback language links still work. No external translation service is called.

The product image is an unchanged real app preview of a fictional side-project discussion. Interactive examples are labeled illustrations. The app is not released; only add a download link after release.

# actualist.app

Static homepage for [Actualist](https://github.com/sporez/actualist), a native iPhone and iPad client for Actual Budget.

No build step. The published tree is `public/`.

## Local

```sh
python3 -m http.server -d public 8080
```

Then open <http://127.0.0.1:8080/>.

## Cloudflare Pages

1. Push this repository to GitHub.
2. In Cloudflare Pages, create a project from that repo.
3. Build command: empty.
4. Output directory: `public`.
5. Attach `actualist.app`.

The site is live at https://actualist.app. TestFlight stays linked from the page (`https://testflight.apple.com/join/HDG6PcGX`).

Optional CLI deploy:

```sh
npx wrangler pages deploy public --project-name actualist
```

## Assets

Screenshots and the app icon are copied from the Actualist repo and resized for the web. If the source shots change, replace `public/assets/*.webp` and `public/assets/icon.png`.

## Public copy

Keep feature and limitation copy in `public/index.html` aligned with the app
repository's `README.md`. Keep every app-policy paragraph and the effective date
in `public/privacy.html` aligned with `../actualist/PRIVACY.md`; retain the
website-specific disclosure separately. Write privacy as a durable data-flow
contract, not a feature-by-feature release summary. The homepage links to
`/privacy`.

The homepage stays short: one-line feature summaries, a Yes / Partial table,
and a link to the app README for full detail. When a limitation changes, update
its table row. The hero's latest-build line is filled in by
`scripts/update-build.py` from the newest `testflight/*` GitHub release. The
`Update latest build` workflow runs it every 3 hours and commits any change,
which redeploys the site. Run it by hand with `python3 scripts/update-build.py`.
Editing these files does not publish them; deployment is a separate step.

`/styles.css` is cached for a day at Cloudflare's edge. Whenever it changes,
bump the `?v=` on its `<link>` in every HTML page, or visitors get new markup
with the old stylesheet.

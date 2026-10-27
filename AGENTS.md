# AGENTS.md

Static site for actualist.app. See `README.md` for layout, deploy, and copy rules.

## Before any work

Run `git pull --rebase` first. The `Update latest build` GitHub Action commits
to `main` on its own whenever a new TestFlight release appears, so a stale
checkout will fail to push or conflict.

## Rules

- No build step. The published tree is `public/`. Pushing `main` deploys through
  Cloudflare Pages.
- When `public/styles.css` changes, bump the `?v=` on its `<link>` in every HTML
  page. Cloudflare caches the stylesheet for a day.
- Keep the header nav and footer identical across `index.html`, `privacy.html`,
  and `404.html`.
- Don't hand-edit the text between `<!-- privacy -->` markers in
  `public/privacy.html`. Change `PRIVACY.md` in the app repo; the workflow
  copies it here when a build containing it is released (`scripts/update-privacy.py`,
  README "Privacy page").
- Don't hand-edit the text between `<!-- build -->` markers. Run
  `python3 scripts/update-build.py` or
  `gh workflow run update-build.yml -R sporez/actualist-web`.
- Keep homepage copy short. Feature details live in the app repo's README.
- Inline scripts and styles are blocked by the CSP in `public/_headers`. Use
  files under `public/`. Adding JavaScript also needs `script-src 'self'` there.
- Screenshots: use the `actualist-sim-screenshots` skill.
- Preview locally with `python3 -m http.server 8080 --bind 0.0.0.0 -d public`.

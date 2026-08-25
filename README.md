# actualist.app

Static homepage for [Actualist](https://github.com/sporez/actualist), a native iPhone client for Actual Budget.

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

The domain currently 302s to TestFlight (`https://testflight.apple.com/join/HDG6PcGX`). Point DNS at this Pages project when the site should take over; TestFlight stays linked from the page.

Optional CLI deploy:

```sh
npx wrangler pages deploy public --project-name actualist
```

## Assets

Screenshots and the app icon are copied from the Actualist repo and resized for the web. If the source shots change, replace `public/assets/*.webp` and `public/assets/icon.png`.

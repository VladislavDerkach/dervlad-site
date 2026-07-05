# dervlad-site

Personal site for Vlad Derkach — [dervlad.com](https://dervlad.com).

Astro 5 + Tailwind v4 + Vercel.

## Local development

```bash
pnpm install
pnpm dev        # http://localhost:4321
pnpm build      # dist/ ready for production
pnpm typecheck  # astro check
```

## Structure

- `src/pages/index.astro` — single-page layout, imports the section components
- `src/components/` — Hero, MetricsBand, Nav, and one component per section (Now, About, Cases, Experience, Builds, Recognition, Contact)
- `src/layouts/BaseLayout.astro` — HTML skeleton with Inter font and OG metadata
- `src/styles/global.css` — Tailwind v4 with design tokens (cream / ink / accent / muted / hairline)
- `src/assets/` — portraits and product screenshots (processed by Astro Image)

## Deployment

Auto-deploy from `main` via Vercel. Domain: dervlad.com (Cloudflare DNS).

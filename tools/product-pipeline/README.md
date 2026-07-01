# FLYLYFE product-image pipeline — snapshot 2026-06-30

Self-contained, **runnable** backup of the hybrid product-image compositor for flylyfe.com.
(Copied out of the Claude session scratchpad so it survives a Claude Code update.)

## What it does
AI-generated blank-tee photos (`blanks/`) + exact print-art PNGs → composited on-model
product images, warped/shaded to look screen-printed into cotton. Output lands in
`~/flylyfe-site/assets/products-model/{handle}-{Color}-{view}.jpg`.

## How to run
```bash
cd ~/Desktop/FLYLYFE/product-pipeline
python3 recompose_all.py                 # re-composite ALL 58 images
python3 recompose_all.py the-signature-tee the-anthem-tee   # just these handles
```
Then deploy: bump `ASSET_V` in `~/flylyfe-site/js/app.js` and `git -C ~/flylyfe-site push`.

## Key files
- **flprod.py** — the `_realistic()` compositor. Locked behaviors (Jorge-driven):
  - `amp=0` → NO displacement warp, so letters keep **straight edges** (not squiggly).
  - `screen` mode (dark shirts): gentle fold-shade + near-opaque → **solid clean white ink**
    (no cracked/mottled washout). `multiply` mode (light shirts): fabric fold-seating so ink
    reads printed-in-cotton, not a flat sticker.
- **recompose_all.py** — master driver: per-design art map + size/cy/x-offset spec. Edit the
  `DESIGNS` dict to retune placement. `F(art,size,cy,xo,ml,md,lc)` where size/cy are fractions.
- **geom_cache.json** / **geometry.json** — grabCut garment geometry per blank (cx, chest_w).
- **blanks/** — 12 AI-gen blank bases (male/female × white/black/ivory × front/back).
  (Also mirrored in `~/flylyfe-site/assets/generated-model-bases/higgsfield/` under different names.)
- **xl/** — processed print art (fixed bold wordmark, fm-final gold stack, signature lockup, etc.).

## Current deployed state (2026-06-30)
- ASSET_V `20260630i-signature`; all **58 images** live; **13 products** on Shopify @ $49.99.
- Compositor fixes shipped: straight edges, solid ink on black, clean gold, corrected wordmark.
- **Signature tee** = left-chest wordmark + back wordmark+tagline lockup (matches Apliiq print);
  rebuilt via `~/flylyfe-apliiq/rebuild_signature.py` (design ids men 5952925-27 / women 5952928-30).
- Final print art: `~/flylyfe-site/assets/print/`. Apliiq build app: `~/flylyfe-apliiq/` (config.py,
  apliiq_build.py, rebuild_signature.py, skumap.json). Neck label id 5951557.

## Only open item
Order **one physical sample** to wash-test print durability + neck tag — the one thing a screen can't confirm.

See memory: `flylyfe-ai-product-images`, `flylyfe-apliiq-api-app`, `project-flylyfe-brand`.

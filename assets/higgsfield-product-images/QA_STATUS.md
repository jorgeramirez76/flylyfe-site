# FlyLyfe Higgsfield Product Image QA Status

Date: 2026-06-29

## Summary

- Removed the previously rejected local-composite/generated product image strategy from active use.
- Generated a full Higgsfield-only GPT Image 2 product set: 58 images, 0 generation failures.
- Regenerated 18 QA-flagged images with stricter logo/text prompts: 18 completed, 0 failures.
- Created contact sheets:
  - `/tmp/flylyfe_higgsfield_products_regen_sheet_1.jpg`
  - `/tmp/flylyfe_higgsfield_products_regen_sheet_2.jpg`
  - `/tmp/flylyfe_higgsfield_products_regen_sheet_3.jpg`

## Accepted in full-resolution spot QA

- `the-after-hours-tee/the-after-hours-tee-Black-back-higgsfield.png`
  - After Hours text/list passed.
- `the-spiritual-thing-tee/the-spiritual-thing-tee-Ivory-back-higgsfield.png`
  - Spiritual Thing text passed.
- `the-house-music-tee/the-house-music-tee-White-front-higgsfield.png`
  - House Music front text passed after regeneration.
- `the-anthem-tee/the-anthem-tee-Black-back-higgsfield.png`
  - FLYLYFE/slogan passed after regeneration.
- `the-conga-tee/the-conga-tee-White-back-higgsfield.png`
  - FLY LYFE/Conga graphic text passed after regeneration.
- `the-signature-tee/the-signature-tee-White-front-higgsfield.png`
  - FLYLYFE + tagline passed after regeneration.
- `the-token-tee/the-token-tee-White-front-higgsfield.png`
  - FLYLYFE / EST. 2007 passed after regeneration.

## Still rejected / do not wire

- `the-token-tee/the-token-tee-Black-front-higgsfield.png`
  - Full-resolution QA: small chest print still has malformed pseudo-glyphs; not acceptable for ecommerce.
- `the-tempo-tee/the-tempo-tee-Black-front-higgsfield.png`
  - Full-resolution QA: chest logo appears like `FLYLUFE`/malformed `FLYLYFE`; not acceptable for ecommerce.

## Nano Banana Pro test

Tested `nano_banana_2` on the two hardest cases:

- Token Tee Black front
- Tempo Tee Black front

Result: both failed full-resolution QA. Nano Banana Pro preserved the curly-haired model/reference, but the small `FLYLYFE` logo still became malformed (`FLVLVFE`-style). Failed test files were removed so they cannot be used accidentally.

## Recommendation before site wiring

Do not wire the Higgsfield folder into the live site yet.

Pure AI generation is still unreliable for very small exact typography on chest logos. For any image where the print text is the product proof, use an exact-art workflow:

1. Higgsfield for realistic model/base/lifestyle.
2. Exact print-art/Printful mockup for typography-critical areas.
3. Manual or programmatic fabric-aware integration only after visual QA.
4. Do not publish until full-resolution QA confirms exact spelling.

If Jorge insists on Higgsfield-only with no local typography correction, regenerate/iterate only the specific rejected images and expect credit burn with uncertain success.

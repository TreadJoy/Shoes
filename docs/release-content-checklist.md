# Release Content Checklist

Run `python manage.py check_release_content` from each deployment-mode
environment before approving a public release. A nonzero exit is a release
blocker; do not suppress it.

## Asset Review

- Every public image, logo, video poster, and product-media file appears in
  `release-content-inventory.json` with its source, rights/consent basis,
  allowed environment, explicit approval status, public-release status,
  checksum, structured metadata-review result, and intentional alt-text
  decision.
- The recorded checksum matches the reviewed file, and the file has no EXIF,
  XMP, IPTC, or comment metadata. A review status of `metadata-present` is a
  release blocker until a clean derivative is approved.
- No AI-generated image is present in the static collection, production media
  storage, or a public template.
- Product media has documented ownership or license, required consents, and no
  unnecessary metadata before it is uploaded.
- The catalog contains only approved active products and variants. Development
  fixtures are inactive and never copied to a public database.

## Content Review

- Replace every development placeholder with approved, factual content before
  launch. Do not approve a release while the command reports a blocked content
  surface.
- Verify community, impact, partner, event, product, pricing, shipping, and
  policy claims against current approved evidence.
- Confirm meaningful images have final alternative text and decorative images
  are intentionally empty-alt.
- Verify all footer, social, legal, support, and contact destinations are
  approved and resolve correctly in the relevant deployment mode.

## Release Evidence

- Attach the command output, asset inventory revision, visual review, and
  owner approval to the release record.
- If unsafe or personal media was removed, verify it is absent from all Git
  refs and hosted repository views before authorizing deployment.

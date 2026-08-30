# Research and Commerce Data Flows

**Policy:** `TJ-PRIV-001` `0.1-draft`
**Status:** Current repository behavior plus explicitly labeled planned services

These diagrams show trust and storage boundaries, not deployed infrastructure.
Dashed nodes are planned or conditional. Provider selection and live validation
remain A2.3/A9 work.

## Research mode

```mermaid
flowchart LR
    B[Visitor browser]
    GF[Google Fonts\ncurrent external request]
    YT[YouTube no-cookie\noptional after activation]
    CF[Cloudflare edge\nplanned]
    DJ[Django research mode]
    RDB[(Research PostgreSQL\naccounts, sessions, waitlist, survey)]
    MED[(Research public R2\napproved public media only\nplanned)]
    MAIL[Email provider\nplanned]
    MON[Redacted monitoring\nplanned]
    STAFF[Authorized research/support staff\nroles not yet enforced]
    B --> GF
    B -. user starts approved video .-> YT
    B --> CF --> DJ
    DJ --> RDB
    DJ -. approved public media .-> MED
    DJ -. approved email .-> MAIL
    DJ -. redacted events .-> MON
    STAFF -. least privilege .-> RDB
    STAFF -. reviewed provider access .-> MAIL
```

Research constraints:

- No cart, order, payment, reservation, Stripe, or commerce-provider path.
- Survey drafts live only in the database session and completed responses are
  created without user/session linkage.
- Waitlist email and optional first name remain directly identifiable.
- No raw research record may enter the commerce database.

## Commerce mode

```mermaid
flowchart LR
    B[Customer browser]
    GF[Google Fonts\ncurrent external request]
    YT[YouTube no-cookie\noptional after activation]
    CF[Cloudflare edge\nplanned]
    DJ[Django commerce mode]
    CDB[(Commerce PostgreSQL\naccounts, sessions, carts, checkout, orders)]
    STRIPE[Stripe hosted Checkout\nshipping + payment boundary]
    CARRIER[Carrier/rate service\nnot selected]
    TAX[Tax provider\nnot selected]
    MAIL[Email provider\nplanned]
    MED[(Commerce public R2\napproved public media only\nplanned)]
    PRIVATE[(Private evidence store\nnot selected)]
    BACKUP[(Encrypted backups/PITR\nplanned, max proposal 35 days)]
    MON[Redacted monitoring\nplanned]
    STAFF[Authorized operations staff\nrole enforcement pending]
    B --> GF
    B -. user starts approved video .-> YT
    B --> CF --> DJ
    DJ --> CDB
    DJ --> STRIPE
    STRIPE -->|signed event; then server retrieves Session| DJ
    DJ -. approved address/tracking fields .-> CARRIER
    DJ -. approved tax fields .-> TAX
    DJ -. approved email .-> MAIL
    DJ -. approved public media .-> MED
    DJ -. approved return evidence .-> PRIVATE
    CDB -. encrypted recovery copy .-> BACKUP
    DJ -. redacted events .-> MON
    STAFF -. least privilege .-> CDB
    STAFF -. separately approved console access .-> STRIPE
```

Commerce constraints:

- Raw card data remains at Stripe; TreadJoy stores only bounded payment,
  refund, amount, currency, state, and reconciliation identifiers.
- Shipping address enters through Stripe-hosted Checkout and is persisted only
  after eligible retrieved-Session verification creates a paid/review order.
- Public media storage is not suitable for returns evidence, exports, customer
  uploads, rights contracts, backups, or incident evidence.
- No raw commerce record may enter research, CI, source control, or content
  production.

## Cross-mode aggregate rule

Any future cross-mode report must be produced from an approved allowlist of
non-identifying aggregate metrics. Before export, remove direct identifiers,
session/internal/provider IDs, free text, precise timestamps/locations, and
small cohorts. The report owner records source data-class IDs, aggregation
logic, minimum cohort rule, purpose, recipient, and retention.

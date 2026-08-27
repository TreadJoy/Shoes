# TreadJoy

## Domain status

The owner confirmed on 2026-08-26 that `tread-joy.com` was purchased through
Cloudflare as TreadJoy's intended base domain. This is a registration record,
not an active-site claim: no public hostname, DNS record, TLS certificate,
managed origin, R2 custom domain, or email service is configured by this
repository change.

`hello@tread-joy.com` and `noreply@tread-joy.com` are reserved future
addresses, not active or monitored mailboxes. The existing `@treadjoy.com`
contact-page and sender-default references are stale launch blockers and remain
unchanged until the email service is configured.

## Commerce Stripe webhook

The commerce deployment's signed webhook endpoint is:

`/orders/stripe/webhook/`

Configure its Stripe Dashboard destination to send these events:

- `checkout.session.completed`
- `checkout.session.async_payment_succeeded`
- `payment_intent.succeeded`
- `refund.created`
- `refund.updated`
- `refund.failed`

Research deployments do not register this route and must not have Stripe
credentials.

When a paid order has insufficient inventory, use the Django admin inventory
allocation queue to review it. Initiate the full refund in Stripe Dashboard,
notify the customer outside the application, then record that notification with
the queue action. Both actions are due by the displayed review deadline. Refund
webhooks update the local audit record and resolve or reopen the queue item.

## Preorder batch operations

Preorder capacity is managed in **Products → Preorder batches** in the Django
admin. Only superusers can create or change a batch.

1. Create the batch in `draft` with its customer-facing carrier-tender window
   and total production capacity.
2. Add an allocation for every active product variant. Combined SKU capacity
   must cover the batch total.
3. Save, then reopen the batch and change it to `open` with a reason. An open
   batch makes that product preorder-only.
4. Use `paused` to stop new checkouts without discarding existing carts. Reopen
   it to resume sales, or use terminal `closed` when the offer is over.

Every status and capacity change is audited. Capacity cannot be reduced below
confirmed commitments, and the promised shipping window becomes read-only after
the first confirmed payment. Stripe refunds do not restore preorder capacity;
that release belongs to the future typed pre-tender cancellation workflow.

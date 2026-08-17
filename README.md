# TreadJoy

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

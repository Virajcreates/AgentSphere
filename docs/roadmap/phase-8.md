# Phase 8 — Billing & Multi-Tenancy Features

## Objectives

Implement subscription management, usage tracking, plan enforcement, and invoice generation. Extend multi-tenancy with self-service capabilities.

## Deliverables

| Deliverable | Description |
|-------------|-------------|
| Subscription Model | `subscription` table with plan_id, status, start/end dates, auto-renew |
| Plan Definition | `plan` table with name, price, limits (conversations, documents, tokens, users, tools) |
| Usage Tracking | Count conversations, messages, tokens, tool calls per tenant per billing cycle |
| Plan Enforcement Middleware | Reject requests that would exceed plan limits; return 402 Payment Required |
| Invoice Generation | Monthly invoice with line items (subscription, overage, credits) |
| Stripe Integration (Optional) | Webhook handler for subscription events (created, updated, cancelled, past_due) |
| Tenant Dashboard API | GET usage, GET current plan, GET invoices, POST upgrade/downgrade |
| Free Trial Logic | Auto-create trial plan on tenant registration; duration configurable |
| Overage Pricing | Per-unit pricing for excess usage above plan limits |
| Unit Tests | Plan limits, usage tracking, invoice calculation, webhook handling |
| Integration Tests | Full billing cycle: subscribe → use → exceed → enforce → invoice |

## Dependencies

- Phase 1 (DB, auth, middleware)
- Phase 6 (analytics aggregation for usage data)
- Stripe SDK (optional; can use direct subscription logic without Stripe)

## Risks

| Risk | Mitigation |
|------|------------|
| Billing bugs causing revenue loss | Usage is append-only; invoices are regenerable; audit trail for corrections |
| Customers exceeding limits before enforcement | Soft warning at 80% usage; hard enforcement at 100%; configurable grace period |
| Stripe webhook failures | Idempotent webhook handling; retry with backoff; manual reconciliation UI |
| Currency/fraud concerns | Use Stripe for payment processing; never handle raw payment data |

## Acceptance Criteria

- [ ] New tenants get a default trial plan with defined limits
- [ ] Usage is tracked per tenant per metric (conversations, documents, tokens)
- [ ] Requests exceeding plan limits are rejected with 429 + reason header
- [ ] Invoice accurately reflects subscription + overage charges
- [ ] Tenant can view usage and invoices via API
- [ ] Plan upgrade/downgrade takes effect at next billing cycle (or immediately if configurable)
- [ ] Stripe subscription events are handled correctly (create, cancel, past_due)
- [ ] All billing operations are audited
# Phase 9 — Additional Transports

## Objectives

Expand the transport layer to support WhatsApp, Slack, Microsoft Teams, Discord, and Email. Each transport calls exactly the same Shared AI Core with no duplicate business logic.

## Deliverables

| Deliverable | Description |
|-------------|-------------|
| Transport Adapter Port | `TransportAdapter(Protocol)` — connect, disconnect, send, receive |
| WhatsApp Transport | WhatsApp Business API integration via Cloud API; webhook handling |
| Slack Bot Transport | Slack Socket Mode or Events API; app mentions, DMs |
| Microsoft Teams Transport | Teams Bot Framework; message extensions, adaptive cards |
| Discord Transport | Discord Bot with slash commands and thread conversations |
| Email Transport | IMAP/SMTP integration; email parsing, reply-threading |
| Channel-Adaptive Response | Transform AI response to channel format (markdown for Slack, cards for Teams, simple text for SMS) |
| Conversation Bridging | Customer can switch channels mid-conversation (WhatsApp → Chat) |
| Attachment Handling | Images, files, voice messages handled per-channel capability |
| Unit Tests | Each transport adapter in isolation |
| Integration Tests | End-to-end test with each channel (using test accounts/mock servers) |

## Dependencies

- Phase 2 (Shared AI Core — all transports call the same workflow)
- Phase 4 (integration tools remain unchanged)
- WhatsApp Business API access
- Slack app with Socket Mode
- Microsoft Teams Bot Framework registration
- Discord Bot token
- Email server (SendGrid, SMTP, or IMAP)

## Risks

| Risk | Mitigation |
|------|------------|
| Platform API changes | Adapter pattern isolates changes; only one adapter affected |
| Rate limits per platform | Per-channel rate limiting; queuing for high-throughput channels |
| Media handling complexity | Downscale to supported formats per channel; reject unsupported with explanation |
| Auth rotation for bots | Credential store with rotation notification; health check alerts on failure |

## Acceptance Criteria

- [ ] WhatsApp message triggers the same LangGraph workflow as web chat
- [ ] Slack bot responds to mentions and DMs
- [ ] Teams bot responds with adaptive cards
- [ ] Discord bot responds to slash commands and threads
- [ ] Email replies are threaded and maintain conversation context
- [ ] Responses are formatted appropriately for each channel
- [ ] Cross-channel bridging preserves conversation history
- [ ] Media is handled appropriately (images sent, audio transcribed, files processed)
- [ ] All transports use the same AI Core — no business logic in any transport
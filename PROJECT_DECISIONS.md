# Project Decisions

## Bot Name

Final name: **Tito Marlon**

Reason:
- Nephews/nieces call John "Tito"
- More endearing for parents
- Sounds like a trusted family member

## Channel Decision

Viber was preferred but not selected for MVP because Viber bot costs appear prohibitive for family-only use.

Selected channel for MVP:

```text
Facebook Messenger
```

## Why Messenger

- Parents/family likely familiar with Facebook/Messenger
- No fixed monthly bot fee like Viber
- Integration works through Meta Developer App
- Current setup is already working

## Why n8n

- Fast orchestration
- Good for webhooks and automation
- Already self-hosted successfully
- Useful for future reminders/calendar/notifications

## Why Move Logic to Code

Memory logic became too complex in n8n.

Backend service is better for:
- Unit tests
- Clear memory extraction
- SQL safety
- Debugging
- Version control
- Future family features

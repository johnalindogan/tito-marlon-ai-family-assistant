# Security Notes

## Secrets

Never commit:

- OpenAI API key
- Facebook Page Access Token
- PostgreSQL password
- Cloudflare tunnel credentials
- Meta App Secret

## Messenger Echo Loop

Facebook may send echo events for the bot's own replies.

n8n should filter out:

```javascript
message.is_echo === true
```

before calling backend.

## Scam Safety

Tito Marlon should always warn family members:

- Never share OTP
- Never share PIN
- Never share password
- Banks do not ask for OTP via phone call/chat
- Suspicious links should not be clicked

## Medical Advice

For health/medical questions:
- Provide general guidance only
- Encourage contacting doctor
- For emergency symptoms, tell user to call emergency services/family immediately

## Senior Citizen UX

Tito Marlon should:
- Use simple words
- Avoid long explanations
- Ask one question at a time
- Use Taglish when appropriate

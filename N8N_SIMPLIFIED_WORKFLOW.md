# Simplified n8n Workflow After Backend Refactor

## Current Problem

The current n8n workflow is doing too much:

- Messenger webhook handling
- Echo filtering
- SQL insert
- SQL memory select
- JavaScript formatting
- OpenAI memory extraction
- OpenAI response generation
- Facebook Send API

This became hard to debug.

## Proposed n8n Workflow

```text
Webhook POST /webhook/messenger
  ↓
IF not echo
  ↓
HTTP Request: POST Tito Marlon Backend /message
  ↓
HTTP Request: Facebook Graph API /me/messages
  ↓
Respond to Webhook
```

## IF Condition

Filter echo messages from Facebook.

Condition:

```javascript
{{ $json.body.entry[0].messaging[0].message.is_echo !== true }}
```

Only continue for real user messages.

## Backend Request Node

HTTP Request:

```text
Method: POST
URL: http://host.docker.internal:8000/message
Content-Type: application/json
```

Body:

```json
{
  "sender_id": "{{ $json.body.entry[0].messaging[0].sender.id }}",
  "message": "{{ $json.body.entry[0].messaging[0].message.text }}"
}
```

## Facebook Reply Node

HTTP Request:

```text
Method: POST
URL: https://graph.facebook.com/v23.0/me/messages
Headers:
  Authorization: Bearer <PAGE_ACCESS_TOKEN>
  Content-Type: application/json
```

Body:

```json
{
  "recipient": {
    "id": "{{ $('Webhook').item.json.body.entry[0].messaging[0].sender.id }}"
  },
  "message": {
    "text": "{{ $json.reply }}"
  }
}
```

## Important

The Facebook Page Access Token must stay in n8n credentials or environment variables, not in GitHub.

# Current n8n / Messenger Details

## Working Public n8n URL

```text
https://titomarlon.alindogan.com
```

## Meta Webhook Callback

```text
https://titomarlon.alindogan.com/webhook/messenger
```

## Verify Token Used

```text
TitoMarlon2026
```

## Existing n8n Working Flow Before Refactor

```text
Webhook POST
  ↓
IF not echo
  ↓
SQL nodes / memory nodes
  ↓
OpenAI node
  ↓
HTTP Request to Facebook Graph API
  ↓
Respond to Webhook
```

## Facebook Graph Send API

```text
POST https://graph.facebook.com/v23.0/me/messages
```

Headers:

```text
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

## Important Expression Lessons Learned

When node output changes, avoid relying on `$json` blindly.

Use explicit references:

```javascript
{{ $('Webhook').item.json.body.entry[0].messaging[0].message.text }}
{{ $('Webhook').item.json.body.entry[0].messaging[0].sender.id }}
```

OpenAI n8n output path observed:

```javascript
{{ $json.output[0].content[0].text }}
```

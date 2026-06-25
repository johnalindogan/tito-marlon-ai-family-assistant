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
Immediate 200 OK to Meta
  ↓
IF not echo
  ↓
HTTP Request: POST Tito Marlon Backend /message
  ↓
HTTP Request: Facebook Graph API /me/messages
```

## IF Condition

Filter echo messages from Facebook.

Condition:

```javascript
{{ $json.body.entry[0].messaging[0].message.is_echo !== true }}
```

Only continue for real user messages.

## Webhook Response Mode

The Messenger webhook must acknowledge Meta immediately. Configure the Webhook node
with `responseMode: onReceived` and HTTP `200`.

Do not wait until after OpenAI, Facebook Send API, or image attachment sends to respond
to the webhook. Waiting until the end can cause Meta retries, duplicate replies, delayed
replies, or messages that appear skipped.

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
  "message": "{{ $json.body.entry[0].messaging[0].message.text || '' }}",
  "image_urls": "{{ image attachment payload URLs, max 3 }}"
}
```

Current n8n raw JSON body must be one expression that serializes the full object.
Do not put `{{ ... }}` inside quoted JSON string values for user text or AI replies;
quotes and newlines can make the node fail with "JSON Body is not valid JSON".

```javascript
={{ JSON.stringify({
  sender_id: $('Webhook').item.json.body.entry[0].messaging[0].sender.id,
  message: $('Webhook').item.json.body.entry[0].messaging[0].message?.text || '',
  image_urls: (($('Webhook').item.json.body.entry[0].messaging[0].message?.attachments || [])
    .filter(attachment => attachment.type === 'image' && attachment.payload && attachment.payload.url)
    .map(attachment => attachment.payload.url)
    .slice(0, 3)),
  messenger_profile: $json.first_name ? {
    first_name: $json.first_name || '',
    last_name: $json.last_name || '',
    profile_pic: $json.profile_pic || '',
    locale: $json.locale || '',
    timezone: $json.timezone ?? null
  } : null
}) }}
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

```javascript
={{ JSON.stringify({
  recipient: {
    id: $('Webhook').item.json.body.entry[0].messaging[0].sender.id
  },
  message: {
    text: $json.reply || 'Pasensya po, may technical issue ako ngayon. Pakisubukan po ulit.'
  }
}) }}
```

## Outbound Image Reply Node

The image branch runs after the text reply node, so do not use `$json.outbound_image_urls`
there. At that point `$json` is the Facebook Send API response. Use an explicit backend
node reference instead:

```javascript
{{ $('Tito Marlon Backend').item.json.outbound_image_urls }}
```

The outbound image condition should check:

```javascript
{{ String(($('Tito Marlon Backend').item.json.outbound_image_urls || []).length > 0) }}
```

Send each outbound image as a real Messenger image attachment, not as a generic card.
Use the same JSON-safe expression pattern:

```javascript
={{ JSON.stringify({
  recipient: {
    id: $('Webhook').item.json.body.entry[0].messaging[0].sender.id
  },
  message: {
    attachment: {
      type: 'image',
      payload: {
        url: $('Tito Marlon Backend').item.json.outbound_image_urls[0],
        is_reusable: true
      }
    }
  }
}) }}
```

If there are multiple image attachment nodes, guard every optional image slot before
sending it. Image 2 must check `length > 1`, and image 3 must check `length > 2`.
Otherwise the workflow can fail by trying to send an undefined URL.

## John Escalation Node

When `/message` returns `escalation_request`, n8n should notify John with a separate
Facebook Send API call. Branch this directly from `Tito Marlon Backend`, not after the
image-send chain, so John is notified even if a later media node has an issue.

Condition:

```javascript
{{ String(!!$('Tito Marlon Backend').item.json.escalation_request) }}
```

Message body:

```javascript
={{ JSON.stringify({
  recipient: {
    id: '<JOHN_MESSENGER_SENDER_ID>'
  },
  message: {
    text: [
      'Tito Marlon escalation',
      `Reason: ${$('Tito Marlon Backend').item.json.escalation_request.reason}`,
      `Urgency: ${$('Tito Marlon Backend').item.json.escalation_request.urgency}`,
      `Summary: ${$('Tito Marlon Backend').item.json.escalation_request.summary}`,
      `Suggested action: ${$('Tito Marlon Backend').item.json.escalation_request.suggested_action}`
    ].join('\n')
  }
}) }}
```

## Important

The Facebook Page Access Token must stay in n8n credentials or environment variables, not in GitHub.

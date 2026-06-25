# Tito Marlon Backend API Spec

## Health Check

### GET `/health`

Response:

```json
{
  "status": "ok"
}
```

## Process Message

### POST `/message`

Request:

```json
{
  "sender_id": "26741790695498132",
  "message": "Ano ang paborito kong pagkain?"
}
```

Response:

```json
{
  "reply": "Paborito mong pagkain ay Sinigang.",
  "memories_saved": []
}
```

## Error Handling

Return `400` if:
- `sender_id` missing
- `message` missing
- `message` not text

Return `500` for server/internal errors.

Avoid returning stack traces in production.

## Notes

The backend should be independent of Facebook payload format. n8n should convert Facebook payload to backend request format.

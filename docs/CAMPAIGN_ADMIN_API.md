# Campaign Admin API

This document describes the administrative API endpoints used by the web UI to manage campaigns (create, edit, delete, publish, schedule, and inspect results).

All endpoints are assumed to be mounted under `/admin/campaigns` and require admin authentication (JWT with admin role). Replace paths as needed to match your router (e.g. `app/api/campaign_admin.py`).

## Authentication
- Header: `Authorization: Bearer <access_token>`
- Admin-only: calls return `403 Forbidden` for non-admin users.

## Common response shapes
- Success envelope: returns resource or list directly (HTTP code indicates success).
- Errors: standard JSON error body `{ "detail": "message" }`.

## List campaigns

- Method: GET
- Path: `/admin/campaigns`
- Query params:
  - `status` (optional): filter by `draft|active|paused|ended|scheduled`
  - `search` (optional): text search on title or description
  - `page` (optional, default 1)
  - `per_page` (optional, default 20)
- Auth: admin
- Response 200: list of campaign objects with pagination metadata in headers or response (choose one). Example body:

```json
{
  "items": [ {"id": "...", "title": "...", "status": "active", "starts_at": "...", "ends_at": "..."} ],
  "page": 1,
  "per_page": 20,
  "total": 123
}
```

## Create campaign

- Method: POST
- Path: `/admin/campaigns`
- Auth: admin
- Body (application/json):

```json
{
  "title": "Summer Promo",
  "description": "Short description / HTML allowed",
  "type": "survey|giveaway|discount", 
  "status": "draft|scheduled|active", 
  "starts_at": "2026-06-10T08:00:00Z", 
  "ends_at": "2026-06-20T23:59:59Z",
  "metadata": { /* optional provider-specific fields */ },
  "questions": [
    {"id": "q1", "type": "text|choice", "label": "What do you like?", "options": ["A","B"] }
  ]
}
```

- Validation rules:
  - `title` required, max length 255
  - `starts_at` < `ends_at` when provided
  - `type` must be supported by backend
  - `status=active` only allowed if schedule is valid and required resources exist

- Responses:
  - `201 Created` with created campaign object
  - `400 Bad Request` with validation errors

## Get campaign details

- Method: GET
- Path: `/admin/campaigns/{id}`
- Auth: admin
- Response 200: full campaign object including questions, participation stats, audit fields
- Response 404: campaign not found

## Update campaign

- Method: PUT
- Path: `/admin/campaigns/{id}`
- Auth: admin
- Body: same as Create (full update). For partial updates use PATCH.
- Response 200: updated campaign
- Response 400/404/403 as appropriate

## Partial update (status or schedule)

- Method: PATCH
- Path: `/admin/campaigns/{id}`
- Auth: admin
- Body examples:
  - Change status:

```json
{ "status": "paused" }
```

  - Reschedule:

```json
{ "starts_at": "2026-06-12T08:00:00Z", "ends_at": "2026-06-22T23:59:59Z" }
```

- Response 200: updated campaign

## Delete campaign

- Method: DELETE
- Path: `/admin/campaigns/{id}`
- Auth: admin
- Response 204: deleted
- Response 404: not found
- Notes: consider soft-delete (mark as `deleted`) so participations and results are preserved for reporting.

## Publish / Unpublish

- Method: POST
- Path: `/admin/campaigns/{id}/publish` (or `/unpublish`)
- Auth: admin
- Body: optional `{ "force": true }`
- Description: moves campaign from `draft`/`scheduled` to `active` if all checks pass; returns 200 with campaign or 400 with failing checks.

## Get participation stats / results

- Method: GET
- Path: `/admin/campaigns/{id}/results`
- Auth: admin
- Query params: `from`, `to`, `group_by` (optional)
- Response 200: aggregated results shape depends on campaign type. Example:

```json
{
  "campaign_id": "...",
  "total_participations": 123,
  "responses": { "q1": { "A": 10, "B": 20 } }
}
```

## Export participations

- Method: GET
- Path: `/admin/campaigns/{id}/export?format=csv`
- Auth: admin
- Response 200: `text/csv` download with participations and metadata

## Error codes
- 400 Bad Request — validation failed
- 401 Unauthorized — missing/invalid token
- 403 Forbidden — not admin or action disallowed (e.g., publish without schedule)
- 404 Not Found — resource missing

## UI considerations
- Create / Edit form fields: `title`, `description` (rich text), `type` (select), `questions` (dynamic list builder), `start`/`end` datetime picker, `status` selector, `attachments` (images/media), `metadata` JSON editor for advanced settings.
- Validations are best mirrored client-side for faster feedback; enforce again server-side.
- Preview: support previewing campaign as a user would see it (render questions and apply scheduling logic).
- Bulk actions: list view should support bulk publish/unpublish/delete.
- Audit: show `created_by`, `created_at`, `updated_by`, `updated_at` in details view.
- Scheduling UI: show timeline and warnings if schedules overlap or are in the past.

## Examples

- Create campaign (curl):

```bash
curl -X POST "https://api.example.com/admin/campaigns" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Summer Promo","type":"survey","status":"draft"}'
```

- Update status to active:

```bash
curl -X PATCH "https://api.example.com/admin/campaigns/abcd-1234" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"active"}'
```

## Mapping to backend
- Suggested router: `app/api/campaign_admin.py` with endpoints above. Use same models as public `campaign_v2` endpoints but restrict access and include admin-only fields (audit, stats).

## Next steps for integration
- Implement server endpoints mirroring these shapes.
- Add tests for admin flows: create, edit, publish, delete, export.
- Connect UI components: list, form, details, results, export.

---
Generated on 2026-06-01.

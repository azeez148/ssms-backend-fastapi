# Campaign Module API Documentation

Base URL: `/campaigns`

All request and response bodies use `camelCase` for property names.

## 1. Campaign Management

### List Campaigns
`GET /all`
- **Query Parameters:**
  - `page` (int, default: 1)
  - `size` (int, default: 10)
  - `search` (string, optional): Search by name or description.
  - `status` (string, optional): Filter by status (`Draft`, `Active`, `Inactive`, `Closed`, `Completed`).
- **Response:**
  ```json
  {
    "items": [
      {
        "id": 1,
        "name": "Summer Tournament",
        "slug": "summer-tournament",
        "status": "Active",
        "totalParticipants": 10,
        "totalSubmissions": 5,
        ...
      }
    ],
    "total": 1,
    "page": 1,
    "size": 10
  }
  ```

### Get Campaign Stats
`GET /stats`
- **Response:**
  ```json
  {
    "totalCampaigns": 5,
    "activeCampaigns": 2,
    "totalParticipants": 150,
    "totalSubmissions": 120,
    "winnersAnnounced": 10
  }
  ```

### Get Campaign Details
`GET /{campaign_id}`
- **Response:** Detailed campaign object including `questions`.

### Create Campaign
`POST /create`
- **Request Body:** `CampaignCreate` schema (supports nested `questions`).
- **Response:** The created campaign object.

### Create Bulk Campaigns
`POST /bulk-create`
- **Request Body:** Array of `CampaignCreate` objects.
- **Response:** Array of created campaign objects.

### Update Campaign
`PUT /update/{campaign_id}`
- **Request Body:** `CampaignUpdate` schema.

### Update Status
`PUT /{campaign_id}/status`
- **Request Body:** `{"status": "Active"}`

### Upload Banner
`POST /{campaign_id}/upload-banner?banner_type=desktop`
- **Query Parameters:** `banner_type` (`desktop` or `mobile`)
- **Body:** Multi-part form data with `file`.

### Upload Promotional Image
`POST /{campaign_id}/upload-image`
- **Body:** Multi-part form data with `file`.

---

## 2. Questions

### Get Questions
`GET /{campaign_id}/questions`
- **Response:** Array of `CampaignQuestionResponse`.

### Save/Overwrite Questions
`POST /{campaign_id}/questions`
- **Request Body:** Array of `CampaignQuestionCreate`.
- **Response:** Updated array of questions.

---

## 3. Participants

### List Participants
`GET /{campaign_id}/participants`
- **Query Parameters:** `page`, `size`, `search`.
- **Response:** Paged list of participants.

### Add Participant (Join)
`POST /{campaign_id}/participants`
- **Request Body:** `{"participantName": "John Doe", "email": "john@example.com", ...}`

### Remove Participant
`DELETE /{campaign_id}/participants/{participant_id}`

### Submit Entry
`POST /{campaign_id}/submit`
- **Request Body:** `{"participantId": 123}`
- **Effect:** Updates `submissionStatus` to `Submitted` and increments `totalSubmissions`.

### Export Participants
`GET /{campaign_id}/participants/export`
- **Response:** Excel file download.

---

## 4. Winners

### Get Winners
`GET /{campaign_id}/winners`
- **Query Parameters:** `winner_type` (optional).

### Assign Winner
`POST /{campaign_id}/winners`
- **Request Body:** `CampaignWinnerCreate`.

### Remove Winner
`DELETE /{campaign_id}/winners/{winner_id}`

---

## 5. Communications

### Trigger Communication
`POST /{campaign_id}/communicate`
- **Request Body:** `CampaignCommunicationCreate`.

### Get Communication History
`GET /{campaign_id}/communications`

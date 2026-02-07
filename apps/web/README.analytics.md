# Analytics page

This app includes an `/analytics` page that:

- calls the backend `GET /analyze`
- receives AI-generated TSX + data
- renders it in a sandbox preview

## Setup

Set an env var when running `apps/web`:

```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

Then visit `http://localhost:3000/analytics`.


# Red Flags API Documentation

## Overview

The Red Flags API analyzes applicant data and identifies potential lending risks based on predefined business rules. It returns detected red flags along with severity levels and color mappings for frontend display.

---

## Endpoint 1: Generate Red Flags

### URL

POST /api/redflags

### Request Body

```json
{
  "application_id": "APP-000001"
}

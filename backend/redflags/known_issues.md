# Known Issues

## 1. Render Free Tier Cold Start

The deployed API may enter sleep mode after a period of inactivity on the Render free tier.

Impact:

* First request may take 20–30 seconds.
* Subsequent requests perform normally.

Workaround:

* Open the `/docs` endpoint before demonstrations.

---

## 2. Dataset Dependency

The Red Flags API depends on the availability of loan and bureau datasets.

Impact:

* Missing or corrupted datasets will prevent flag generation.

Workaround:

* Verify dataset files exist before deployment.

---

## 3. Network Connectivity

External network issues may temporarily affect access to the deployed API.

Impact:

* API requests may fail even when the application is healthy.

Workaround:

* Retry requests and verify Render service status.

---

## 4. CORS Configuration

Frontend applications from unauthorized origins may be blocked.

Impact:

* Browser requests can fail due to CORS restrictions.

Workaround:

* Add approved frontend origins in the FastAPI CORS middleware configuration.

---

## Maintainer

Guru Prasad Sai

CreditSentinel – Red Flags Module

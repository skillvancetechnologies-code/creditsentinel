# Red Flags API Deployment Runbook

## Purpose

This document describes how to run, deploy, and troubleshoot the CreditSentinel Red Flags API.

---

## Local Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start API

```bash
uvicorn red_flag_api:app --reload
```

### Access Swagger Documentation

```text
http://127.0.0.1:8000/docs
```

---

## Deployment Process

1. Make code changes locally.
2. Test endpoints using Swagger.
3. Commit changes to Git.

```bash
git add .
git commit -m "Update Red Flags API"
git push origin main
```

4. Push code to the official CreditSentinel repository.
5. Render automatically redeploys the latest version.

---

## Verification After Deployment

Verify:

* `/api/redflags`
* `/api/redflags-batch`
* Swagger documentation loads successfully.
* No deployment errors in Render logs.

---

## Rollback Procedure

If deployment fails:

1. Revert the last commit.
2. Push the reverted code.
3. Trigger redeployment on Render.
4. Verify endpoints are functioning correctly.

---

## Common Issues

### Render Cold Start

Free Render services may sleep after inactivity.

Solution:

* Open the `/docs` endpoint before demonstrations.

### CORS Errors

Ensure CORS middleware is enabled and frontend origin is allowed.

### Dataset Loading Issues

Verify all required CSV files exist in the deployment environment.

---

CreditSentinel – Red Flags Module


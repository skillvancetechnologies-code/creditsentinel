# DEPLOYMENT_RUNBOOK

## Objective

Deploy CreditSentinel to Render production environment safely and consistently.

Estimated Deployment Time: 15 Minutes

---

## Pre-Deployment Checklist

* All code committed to GitHub
* Repository synchronized with origin/main
* Production readiness assessment completed
* Environment variables documented
* No open critical blockers
* Latest tests passing

---

## Deployment Procedure

### Step 1 — Verify GitHub Repository

```bash
git status
git pull origin main
git log --oneline -3
```

Confirm:

* Working tree clean
* Latest changes pushed
* Correct branch selected

---

### Step 2 — Log Into Render

1. Open Render Dashboard
2. Select CreditSentinel service
3. Verify environment configuration
4. Confirm production service status

---

### Step 3 — Configure Environment Variables

Required Variables:

```text
DATABASE_URL=
GROQ_API_KEY=
ENVIRONMENT=production
LOG_LEVEL=INFO
```

Verify all variables are present before deployment.

---

### Step 4 — Deploy Latest Version

1. Select "Manual Deploy"
2. Choose latest commit
3. Start deployment
4. Monitor build logs

Expected deployment duration:
5–10 minutes

---

### Step 5 — Post Deployment Validation

Verify:

* API service running
* Database connectivity successful
* Health endpoint responding
* Memo generation operational
* Risk scoring operational
* Red Flag detection operational

---

## Database Validation

Check:

* Database reachable
* Tables available
* Application startup successful
* No migration failures

---

## Rollback Procedure

If deployment fails:

### Immediate Actions

1. Stop current deployment
2. Identify failing component
3. Review deployment logs

### Rollback

1. Open Render dashboard
2. Select previous successful deployment
3. Redeploy previous version
4. Validate service health

### Validation

Confirm:

* Error rate normal
* Latency normal
* Endpoints responding
* Database operational

---

## Success Criteria

Deployment considered successful when:

* Service healthy
* Error rate below 1%
* Monitoring active
* No critical alerts generated
* User workflows functioning

Status: APPROVED FOR PRODUCTION DEPLOYMENT


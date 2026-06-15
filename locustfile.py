from locust import HttpUser, task, between
import random

class CreditSentinelUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def applications_list(self):
        self.client.get(
            "/api/applications",
            name="applications_list"
        )

    @task
    def application_detail(self):
        app_id = f"APP-{random.randint(1,100):06d}"

        self.client.get(
            f"/api/applications/{app_id}",
            name="application_detail"
        )

    @task
    def risk_score(self):
        app_id = f"APP-{random.randint(1,100):06d}"

        self.client.post(
            "/api/score",
            json={"application_id": app_id},
            name="risk_score"
        )

    @task
    def decision_submit(self):
        app_id = f"APP-{random.randint(1,100):06d}"

        self.client.post(
            f"/api/applications/{app_id}/decision",
            json={
                "decision": "APPROVE",
                "notes": "Load Test"
            },
            name="decision_submit"
        )

    @task
    def portfolio_summary(self):
        self.client.get(
            "/api/portfolio/summary",
            name="portfolio_summary"
        )
        

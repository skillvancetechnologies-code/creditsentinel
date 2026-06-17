from locust import HttpUser, task, between

class CreditUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def call_score_api(self):
        self.client.post(
            "/api/score",
            json={"application_id": f"test_user_1"},
            headers={"Content-Type": "application/json"})

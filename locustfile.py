from locust import HttpUser, task, between

class CreditSentinelUser(HttpUser):

    wait_time = between(1, 3)

    @task
    def get_application(self):
        self.client.get("/api/applications/APP-000001")
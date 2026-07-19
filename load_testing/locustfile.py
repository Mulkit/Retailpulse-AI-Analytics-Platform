"""
RetailPulse — Load test.

Hits the dashboard's health endpoint and the static page shells for each
route (the SPA shell load is what a load balancer / CDN would actually be
serving repeatedly; the per-session script execution happens over websocket
and isn't meaningfully load-testable via plain HTTP).
"""
from locust import HttpUser, task, between


class DashboardUser(HttpUser):
    wait_time = between(1, 3)

    @task(5)
    def health_check(self):
        self.client.get("/_stcore/health", name="/_stcore/health")

    @task(3)
    def home_page(self):
        self.client.get("/", name="/ (Home)")

    @task(2)
    def demand_forecast_page(self):
        self.client.get("/Demand_Forecast", name="/Demand_Forecast")

    @task(2)
    def churn_risk_page(self):
        self.client.get("/Churn_Risk", name="/Churn_Risk")

    @task(1)
    def inventory_health_page(self):
        self.client.get("/Inventory_Health", name="/Inventory_Health")

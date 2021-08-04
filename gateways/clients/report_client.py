class ReportClient:

    def send(self, message: str) -> bool:
        print(f"Report sent! Message: {message}")
        return True

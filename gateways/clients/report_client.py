class ReportClient:

    def send(self, message: str) -> bool:
        """Send report

        :param message: message to be sent
        :type message: str
        :return: if report was successful sent or not
        :rtype: bool
        """
        print(f"Report sent! Message: {message}")  # TODO: THis line will be changed to real messenger provider
        return True

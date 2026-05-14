import requests


class APIClient:

    def __init__(self, base_url: str):

        self.s = requests.Session()
        self.base_url = base_url

    def post(self, path: str, json: dict):

        return self.s.post(
            f"{self.base_url}{path}",
            json=json
        )

    def delete(self, path: str):

        return self.s.delete(
            f"{self.base_url}{path}"
        )

    def get(self, path: str):

        return self.s.get(
            f"{self.base_url}{path}"
        )
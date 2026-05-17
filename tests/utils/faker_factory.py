from faker import Faker

fake = Faker("vi_VN")


class UserFactory:
    """Sinh dữ liệu người dùng ngẫu nhiên hợp lệ."""

    @staticmethod
    def valid_user() -> dict:
        return {
            "full_name": fake.name(),
            "email": fake.unique.email(),
            "password": "Test@1234",
            "confirm_password": "Test@1234",
        }

    @staticmethod
    def valid_email() -> str:
        return fake.unique.email()

    @staticmethod
    def valid_password() -> str:
        return "Test@1234"
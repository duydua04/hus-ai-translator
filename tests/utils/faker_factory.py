from faker import Faker


def get_faker(locale: str = "vi_VN"):
    return Faker(locale)

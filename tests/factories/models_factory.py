from faker import Faker

faker = Faker()


class Category:
    def __init__(
        self,
        id_: int,
        name: str,
        slug: str,
        is_active: bool,
        level: int,
        parent_id: int,
    ):
        self.id = id_
        self.name = name
        self.slug = slug
        self.is_active = is_active
        self.level = level
        self.parent_id = parent_id


def get_random_category_dict(id_: int = None):
    return {
        "id": id_ or faker.random_int(1, 1000),
        "name": faker.word(),
        "slug": faker.slug(),
        "is_active": faker.boolean(),
        "level": faker.random_int(1, 20),
        "parent_id": None,
    }

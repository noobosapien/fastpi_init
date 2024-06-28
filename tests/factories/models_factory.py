from faker import Faker
from itertools import count

faker = Faker()

id_counter = count(start=1)


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
    id_counter = count(1)
    id_ = next(id_counter)

    return {
        "id": id_,
        "name": faker.word(),
        "slug": faker.slug(),
        "is_active": faker.boolean(),
        "level": faker.random_int(1, 20),
        "parent_id": None,
    }

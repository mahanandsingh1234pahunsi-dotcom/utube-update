verified_users = set()


def is_verified(user_id: int) -> bool:
    return user_id in verified_users


def verify_user(user_id: int):
    verified_users.add(user_id)

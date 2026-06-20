from modules.auth import authenticate_user, register_new_user
from modules.database import delete_user, get_user_by_email, list_users


def test_user_registration_and_login():
    email = "unit_test_user@campusgpt.edu"
    password = "secret_password"
    name = "Test User"

    # 1. Clean up first if user exists
    existing = get_user_by_email(email)
    if existing:
        delete_user(existing["id"])

    # 2. Register User
    status = register_new_user(name, email, password)
    assert status == "success"

    # 3. Prevent Duplicates
    status_duplicate = register_new_user(name, email, password)
    assert status_duplicate == "exists"

    # 4. Authenticate User with correct credentials
    user = authenticate_user(email, password)
    assert user is not None
    assert user["name"] == name
    assert user["email"] == email

    # 5. Fail authentication with wrong password
    user_fail = authenticate_user(email, "wrong_password")
    assert user_fail is None

    # 6. Verify user in list
    all_users = list_users()
    emails = [u["email"] for u in all_users]
    assert email in emails

    # 7. Delete User and verify removal
    delete_user(user["id"])
    user_deleted = authenticate_user(email, password)
    assert user_deleted is None

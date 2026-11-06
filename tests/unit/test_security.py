from security import hash_password, verify_password

def test_password_can_be_hashed_and_verified():
    password = "12345"
    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True
    assert verify_password("WrongPassword", password_hash) is False
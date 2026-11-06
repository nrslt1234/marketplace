def calculate_price(price, discount):
    return price - price * discount / 100

def test_calculate_price():
    # Arrange — подготавливаем данные
    price = 1000
    discount = 10
    expected = 900

    # Act — вызываем то, что тестируем
    result = calculate_price(price, discount)

    # Assert — проверяем результат
    assert result == expected


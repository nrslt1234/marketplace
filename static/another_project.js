// Функции для работы с количеством
function changeQuantity(delta) {
    const input = document.getElementById('quantity');
    let value = parseInt(input.value) + delta;
    if (value < 1) value = 1;
    if (value > 10) value = 10;
    input.value = value;
}

// Покупка сейчас
function buyNow() {
    const quantity = document.getElementById('quantity').value;
    alert(`Переход к оформлению заказа: ${productData.name} (${quantity} шт.)`);
    // Редирект на страницу оформления заказа
}

// Заполнение похожих товаров
function renderRelatedProducts() {
    const container = document.getElementById('relatedProducts');
    container.innerHTML = relatedProducts.map(product => `
        <div class="product-card" onclick="window.location.href='/product/${product.id}'">
            <img src="${product.photo}" alt="${product.name}">
            <div class="product-card-content">
                <h3>${product.name}</h3>
                <div class="price">${product.price.toLocaleString()} ₽</div>
            </div>
        </div>
    `).join('');
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Обновляем статус доступности
    const availabilityBadge = document.getElementById('availabilityBadge');
    if (!productData.availability) {
        availabilityBadge.textContent = 'Нет в наличии';
        availabilityBadge.classList.add('out-of-stock');
        document.getElementById('addToCartBtn').disabled = true;
    }

    renderRelatedProducts();
});

// Показ уведомления вместо alert
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check' : 'exclamation'}"></i>
        ${message}
    `;

    // Стили для уведомления (добавить в CSS)
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#2a9d8f' : '#e63946'};
        color: white;
        padding: 1rem 2rem;
        border-radius: 5px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}


//Метод для Избранного
async function addToFav(product_id) {

    const basketData = {
        product_id: product_id,
        client_id: 1
    };

    try {
        const response = await fetch('/favourites', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(basketData)
        });

        if (response.ok) {
            showNotification(`Товар добавлен в Избранное`);
        } else {
            showNotification('Ошибка при добавлении товара', 'error');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Произошла ошибка', 'error');
    }
}




// Использование уведомления вместо alert
async function addToCart(product_id) {
    const quantity = parseInt(document.getElementById('quantity').value);

    const basketData = {
        product_id: product_id,
        amount: quantity,
        client_id: 1
    };

    try {
        const response = await fetch('/basket', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(basketData)
        });

        if (response.ok) {
            showNotification(`Товар добавлен в корзину (${quantity} шт.)`);
        } else {
            showNotification('Ошибка при добавлении товара', 'error');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Произошла ошибка', 'error');
    }
}
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check' : 'exclamation'}"></i>
        ${message}
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}
        // Обновление количества товара
async function updateQuantity(itemId, change) {
    const input = document.getElementById(`quantity-item${itemId}`);
    let newValue = parseInt(input.value) + change;

    if (newValue < 1) newValue = 1;
    if (newValue > 10) newValue = 10;

    input.value = newValue;

    // Обновляем итоги корзины
    updateCartTotals();

    const AmountData = {
        product_id: itemId,
        amount: newValue
    };

    try {
        const response = await fetch('/amount/new', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(AmountData)
        });

        if (response.ok) {
            console.log('Количество изменено');
        } else {
            const errorData = await response.json();
            showNotification(errorData.detail || 'Ошибка при изменении количества', 'error');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Произошла ошибка сети', 'error');
    }
}

// Удаление товара из корзины
function removeItem(itemId) {
    const item = document.getElementById(itemId);
    item.style.opacity = '0';
    item.style.transform = 'translateX(-20px)';

    setTimeout(() => {
        item.remove();
        updateCartTotals(); // обновляем сумму и количество после удаления

        const cartItems = document.querySelector('.cart-items');
        if (cartItems.children.length === 0) {
            showEmptyState();
        }
    }, 300);
}

// Обновление итоговой суммы и количества товаров
function updateCartTotals() {
    let itemsTotal = 0;
    let itemsCount = 0;

    document.querySelectorAll('.cart-item').forEach(item => {
        const quantity = parseInt(item.querySelector('.quantity-input').value);
        const price = parseInt(item.querySelector('.item-price').textContent.replace(/[^\d]/g, ''));
        itemsTotal += price * quantity;
        itemsCount += quantity;
    });

    document.getElementById('itemsTotal').textContent = `${itemsTotal.toLocaleString()}₽`;
    document.getElementById('orderTotal').textContent = `${itemsTotal.toLocaleString()}₽`;

    const badge = document.querySelector('.icon-btn.active .badge');
    if (badge) badge.textContent = itemsCount;

    const itemsCountElement = document.getElementById('itemsCount');
    if (itemsCountElement) itemsCountElement.textContent = itemsCount;
}


// Показ состояния "пусто"
function showEmptyState() {
    const cartContent = document.getElementById('cartContent');
    cartContent.innerHTML = `
        <div class="empty-state">
            <i class="fas fa-shopping-cart"></i>
            <h3>Ваша корзина пуста</h3>
            <p>Добавьте товары в корзину, чтобы сделать заказ</p>
            <a href="catalog.html" class="browse-btn">Перейти в каталог</a>
        </div>
    `;
}

async function SaveOrder (event) {
    event.preventDefault();
    event.stopPropagation(); // 🔥 ДОБАВЛЯЕМ ЭТУ СТРОЧКУ

    console.log('Функция SaveOrder вызвана'); // для отладки



    const datainfo = [];
    // [ {"product_id" : ..., "amount": .. }, {} ]


    const items = document.querySelectorAll(".cart-item");
    items.forEach( item => {
        const amount = item.querySelector(".quantity-input").value;
        const id = item.id.slice(4);

        datainfo.push({
            product_id: id,
            amount: amount
        })
    })


    try {
        const response = await fetch('/basket/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({items: datainfo})
        });

        if (response.ok) {
            console.log('Заказ создан');
            showNotification('Заказ успешно создан!', 'success');
        } else {
            const datainfo_error = await response.json();
            showNotification('Ошибка при сохранении заказа', 'error');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Произошла ошибка сети', 'error');
    }
}


 // Добавляем обработчики для кнопок действий
        document.querySelectorAll('.btn-primary').forEach(btn => {
            if (btn.textContent.includes('Подробнее')) {
                btn.addEventListener('click', function() {
                    alert('Здесь будет открыта страница с деталями заказа');
                });
            }
        });

        document.querySelectorAll('.btn-outline').forEach(btn => {
            if (btn.textContent.includes('Повторить')) {
                btn.addEventListener('click', function() {
                    alert('Товары из заказа добавлены в корзину');
                });
            }


// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    updateCartTotals(); // сразу показываем актуальные итоги и количество
});




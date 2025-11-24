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


async function AuthorizationTo(event) {
    event.preventDefault();
    const login = document.getElementById("login").value;
    const password = document.getElementById("password").value;


    const AuthorizationData = {
        login: login,
        password: password
    };

    try {
        const response = await fetch('/authorization', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(AuthorizationData)
        });

        if (response.ok) {
            data = await response.json()
            console.log(data)
            if (data.status) {
                showNotification(`Пользователь успешно авторизировался!`);
                window.location.href = '/personalaccount'
            } else {
                showNotification('Неверный логин или пароль');
            }
        } else {
            showNotification('Ошибка');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Произошла ошибка', 'error');
    }
}
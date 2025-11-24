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

// 🔥 ДОБАВЛЯЕМ ФУНКЦИЮ ПЕРЕХОДА МЕЖДУ ШАГАМИ
function goToStep(step) {
    console.log(`Переход к шагу ${step}`); // для отладки

    // Скрываем все шаги
    document.querySelectorAll('.step-content').forEach(content => {
        content.style.display = 'none';
    });

    // Обновляем индикаторы шагов
    document.querySelectorAll('.step').forEach(stepEl => {
        stepEl.classList.remove('active', 'completed');
    });

    // Активируем текущий и предыдущие шаги
    for (let i = 1; i <= step; i++) {
        const stepEl = document.getElementById(`step${i}`);
        if (i === step) {
            stepEl.classList.add('active');
        } else {
            stepEl.classList.add('completed');
        }
    }

    // Показываем текущий шаг
    const currentStepElement = document.getElementById(`step${step}Content`);
    if (currentStepElement) {
        currentStepElement.style.display = 'block';
        currentStepElement.classList.add('fade-in');
    }

    // Обновляем информационное сообщение
    updateInfoMessage(step);
}

// 🔥 ФУНКЦИЯ ОБНОВЛЕНИЯ СООБЩЕНИЯ
function updateInfoMessage(step) {
    const messages = {
        1: 'Введите email, указанный при регистрации',
        2: 'Введите 6-значный код, отправленный на вашу почту',
        3: 'Придумайте новый надежный пароль'
    };

    const infoText = document.getElementById('infoText');
    if (infoText && messages[step]) {
        infoText.textContent = messages[step];
    }
}

// 🔥 ФУНКЦИЯ ТАЙМЕРА
function startTimer(duration = 60) {
    let timeLeft = duration;
    const resendLink = document.getElementById('resendLink');
    const timerElement = document.getElementById('timer');

    if (resendLink) resendLink.style.display = 'none';


    const timerInterval = setInterval(() => {
        if (timerElement) {
            timerElement.textContent = `Отправить код повторно через: ${timeLeft} сек`;
        }
        timeLeft--;

        if (timeLeft < 0) {
            clearInterval(timerInterval);
            if (timerElement) timerElement.style.display = 'none';
            if (resendLink) resendLink.style.display = 'block';
        }
    }, 1000);
}



async function CodeTo(event) {
    event.preventDefault();
    event.stopPropagation(); // 🔥 ДОБАВЛЯЕМ ЭТУ СТРОЧКУ

    console.log('Функция CodeTo вызвана'); // для отладки

    const email = document.getElementById("email").value;

    // Валидация email
    if (!email || !isValidEmail(email)) {
        showNotification('Пожалуйста, введите корректный email', 'error');
        return;
    }

    const CodeData = {
        email: email,
    };

    try {
        const response = await fetch('/forgotpasswordcode', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(CodeData)
        });

        if (response.ok) {
        console.log('Код отправлен')
            showNotification(`Код отправлен на ${email}!`);

            // 🔥 НЕМЕДЛЕННЫЙ ПЕРЕХОД БЕЗ setTimeout
            goToStep(2); // Переходим на шаг с вводом кода
            startTimer(); // Запускаем таймер

            // Фокусируемся на первом поле для кода
            const firstCodeInput = document.querySelector('.code-input');
            if (firstCodeInput) firstCodeInput.focus();

        } else {
            const errorData = await response.json();
            showNotification(errorData.detail || 'Ошибка при отправке кода', 'error');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Произошла ошибка сети', 'error');
    }
}

// 🔥 ФУНКЦИЯ ПРОВЕРКИ EMAIL
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}




async function CodeCheck(event) {
    event.preventDefault();
    event.stopPropagation(); // 🔥 ДОБАВЛЯЕМ ЭТУ СТРОЧКУ

    console.log('Функция CodeCheck вызвана'); // для отладки

    const email = document.getElementById("email").value;
    const code = document.getElementById("verificationCode").value;
    // Валидация email
    if (!email || !isValidEmail(email)) {
        showNotification('Пожалуйста, введите корректный code', 'error');
        return;
    }

    const CodeData = {
        email: email,
        code: code
    };

    try {
        const response = await fetch('/forgotpassword/verify/code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(CodeData)
        });

        if (response.ok) {
        console.log('Код проверен')
            showNotification(`Код отправлен на ${email}!`);

            // 🔥 НЕМЕДЛЕННЫЙ ПЕРЕХОД БЕЗ setTimeout
            goToStep(3); // Переходим на шаг с вводом кода
            startTimer(); // Запускаем таймер

            // Фокусируемся на первом поле для кода
            const firstCodeInput = document.querySelector('.code-input');
            if (firstCodeInput) firstCodeInput.focus();

        } else {
            const errorData = await response.json();
            showNotification(errorData.detail || 'Ошибка при проверке кода', 'error');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Произошла ошибка сети', 'error');
    }
}


async function NewPassword(event) {
    event.preventDefault();
    event.stopPropagation(); // 🔥 ДОБАВЛЯЕМ ЭТУ СТРОЧКУ

    console.log('Функция NewPassword вызвана'); // для отладки

    const email = document.getElementById("email").value;
    const new_password_1 = document.getElementById("newPassword").value;
    const new_password_2 = document.getElementById("confirmPassword").value;


    if (new_password_1 !== new_password_2) {
        showNotification('Пароли не совпадают', 'error');
        return;
    }

    const PasswordData = {
        email: email,
        new_password: new_password_1
    };

    try {
        const response = await fetch('/forgotpassword/password/new', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(PasswordData)
        });

        if (response.ok) {
            console.log('Пароль успешно изменен');
            showNotification('Пароль успешно изменен!', 'success');

            // 🔥 ПЕРЕХОД НА СТРАНИЦУ ВХОДА
            setTimeout(() => {
                window.location.href = '/autho';
            }, 2000);

   } else {
            const errorData = await response.json();
            showNotification(errorData.detail || 'Ошибка при изменении пароля', 'error');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Произошла ошибка сети', 'error');
    }
}


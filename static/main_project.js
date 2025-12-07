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
async function searchTo(event) {
    if(event.key == "Enter") {
    const q = document.getElementById("search").value;
    const category = document.getElementById("category").value;
    const page = 1

    const searchData = new URLSearchParams({
        q: q,
        page: page,
        category : category

    }
    );
    window.location.href = `/search?${searchData.toString()}`



//    try {
//        const response = await fetch(`/search?${searchData.toString()}`, {
//            method: 'GET',
//            headers: {
//                'Content-Type': 'application/json',
//            },
//
//        });
//
//        if (response.ok) {
//            showNotification(`Товары найдены`);
//        } else {
//            showNotification('Ошибка при нахождении товаров', 'error');
//        }
//    } catch (error) {
//        console.error('Ошибка:', error);
//        showNotification('Произошла ошибка', 'error');
//    }
    }
}

document.getElementById("search").addEventListener("keydown", searchTo)
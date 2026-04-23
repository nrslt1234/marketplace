// static/js/add-product.js
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("productForm");
    const fileInput = document.getElementById("photo");
    const statusEl = document.getElementById("statusMessage");

    if (!form) return;

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        statusEl.textContent = "";
        statusEl.className = "status";

        const file = fileInput.files[0];
        if (!file) {
            statusEl.textContent = "Пожалуйста, выберите фото";
            statusEl.className = "status error";
            return;
        }

        try {
            // ---- 1. Загрузка фото ----
            const uploadForm = new FormData();
            uploadForm.append("file", file);

            const uploadResponse = await fetch("/upload/photo", {
                method: "POST",
                body: uploadForm,
            });
            if (!uploadResponse.ok) {
                const errText = await uploadResponse.text();
                throw new Error(errText || "Ошибка загрузки фото");
            }
            const { object_key } = await uploadResponse.json();

            // ---- 2. Создание товара ----
            const productData = {
                name: document.getElementById("name").value.trim(),
                price: parseInt(document.getElementById("price").value, 10),
                availability: document.getElementById("availability").checked,
                description: document.getElementById("description").value.trim(),
                photo: object_key,
                category_id: parseInt(document.getElementById("category").value, 10),
            };

            const productResponse = await fetch("/upload/products", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(productData),
            });
            if (!productResponse.ok) {
                const errText = await productResponse.text();
                throw new Error(errText || "Ошибка создания товара");
            }
            const result = await productResponse.json();

            statusEl.textContent = `Товар успешно добавлен! ID: ${result.product_id}`;
            statusEl.className = "status success";

            form.reset();
        } catch (error) {
            statusEl.textContent = error.message;
            statusEl.className = "status error";
        }
    });
});
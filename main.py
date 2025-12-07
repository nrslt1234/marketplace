import os
import random

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

load_dotenv()

import uvicorn
from fastapi import FastAPI, Query
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, insert, or_, and_, update, delete, func
from sqlalchemy.orm import joinedload, selectinload

from DataBase.models import Service, Ourwork, Products, Category, BasketClient, BasketProduct, Favourites, Client, \
    Forgotpasswordcode, Order, Orderproduct
from DataBase.session import SessionLocal

from random import shuffle

from schemas import BasketCreate, FavCreate, RegCreate, AuthoCreate, ForgotCreate, VerifyCode, NewPassword, Newamount, \
    CheckItem, OrderSchema
from security import hash_password, verify_password
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(title="Simple FastAPI App")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(SessionMiddleware, secret_key="super-secret-key")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("///", response_class=HTMLResponse)
def homes(request: Request):
    return templates.TemplateResponse("index_1.html", {"request": request})


@app.get("/project", response_class=HTMLResponse)
def homes(request: Request):
    user = request.session.get("user")
    if user is None:
        user = {"status": False}
    else:
        client_id = user.get("client_id")
        user = get_current_user(client_id)
    with SessionLocal() as session:
        stmt = select(Products)
        products = session.execute(stmt).scalars().all()
        random.shuffle(products)
        #
        stm = select(Category)
        category = session.execute(stm).scalars().all()

    return templates.TemplateResponse("project.html",
                                      {"request": request, "category": category, "products": products[:4],
                                       "user": user})


@app.get("/product/{id}", response_class=HTMLResponse)
def homes(request: Request, id: int):
    with SessionLocal() as session:
        stmt = select(Products).where(Products.id == id)
        product = session.execute(stmt).scalar_one()

    return templates.TemplateResponse("another_project.html", {"request": request, "product": product})


@app.get("/bigweb", response_class=HTMLResponse)
def homes(request: Request):
    # session = SessionLocal()
    # session.close()

    with SessionLocal() as session:
        stmt = select(Service)
        services = session.execute(stmt).scalars().all()

        stmt = select(Ourwork)
        ourworks = session.execute(stmt).scalars().all()

    return templates.TemplateResponse("big_index.html",
                                      {"request": request, "services": services, "ourworks": ourworks})


# Ручка для перехода на страничку личного кабинета при нажатии кнопки ВОЙТИ
@app.get("/enter", response_class=HTMLResponse)
def homes(request: Request):
    return templates.TemplateResponse("enter.html", {"request": request})


@app.post("/amount/new")
def homes(request: Request, data: Newamount):
    with SessionLocal() as session:
        stmt = update(BasketProduct).where(BasketProduct.id == data.product_id).values(amount=data.amount)
        session.execute(stmt)
        session.commit()
    return {"status": True}


@app.post("/basket/save")
def homes(request: Request, data: OrderSchema):
    user = request.session.get("user")
    client_id = user.get("client_id")

    with SessionLocal() as session:
        order = Order(client_id=client_id, status="Оформлен")
        session.add(order)
        session.commit()
        session.flush(order)

        for i in data.items:
            orderproduct = Orderproduct(product_id=i.product_id, amount=i.amount, order_id=order.id)
            session.add(orderproduct)
            session.commit()
            session.flush(orderproduct)
        session.commit()

    with SessionLocal() as session:
        for i in data.items:
            subq = (
                session.query(BasketProduct.id)
                .join(BasketClient)
                .filter(
                    BasketClient.client_id == client_id,
                    BasketProduct.product_id == i.product_id
                )
                .subquery()
            )

            stmt = delete(BasketProduct).where(BasketProduct.id.in_(subq))
            session.execute(stmt)

        session.commit()

    return {"status": True}


@app.post("/basket/remove")
def remove_from_basket(request: Request, data: CheckItem):
    user = request.session.get("user")
    if user is None:
        return {"status": False, "message": "Необходима авторизация"}

    client_id = user.get("client_id")

    with SessionLocal() as session:
        # Находим корзину клиента
        stmt = select(BasketClient).where(BasketClient.client_id == client_id)
        basket_client = session.execute(stmt).scalars().first()

        if basket_client:
            # Удаляем товар из корзины
            stmt = delete(BasketProduct).where(
                and_(
                    BasketProduct.basket_client_id == basket_client.id,
                    BasketProduct.product_id == data.product_id
                )
            )
            session.execute(stmt)
            session.commit()

        return {"status": True, "message": "Товар удален из корзины"}

# Ручка для перехода на страничку ИЗБРАННОЕ при нажатии кнопки Избранное
@app.get("/basket", response_class=HTMLResponse)
def homes(request: Request):
    user = request.session.get("user")
    if user is None:
        return templates.TemplateResponse("authorization.html", {"request": request})
    else:
        client_id = user.get("client_id")
        user = get_current_user(client_id)

    with SessionLocal() as session:
        stmt = (select(BasketProduct)
                .join(Products, BasketProduct.product_id == Products.id)
                .options(selectinload(BasketProduct.product))  # если есть связь relationship
                .join(BasketClient, BasketProduct.basket_client_id == BasketClient.id)
                .options(selectinload(BasketProduct.basket_client))  # если есть связь relationship
                .where(BasketClient.client_id == client_id)
                )
        basketproduct = session.execute(stmt).scalars().all()

        price = 0
        amount = 0
        for goods in basketproduct:
            price += int(goods.product.price.replace(" ", "")) * int(goods.amount)
            amount = int(goods.amount)


    return templates.TemplateResponse("basket.html",
                                      {"request": request, "basketproduct": basketproduct, "user": user, "price": price,
                                       "amount": amount})


@app.post("/basket")
def homes(request: Request, data: BasketCreate):
    user = request.session.get("user")
    if user is None:
        return templates.TemplateResponse("authorization.html", {"request": request})
    else:
        client_id = user.get("client_id")
        user = get_current_user(client_id)

    with SessionLocal() as session:
        stmt = select(BasketClient).where(BasketClient.client_id == client_id)
        basket_client = session.execute(stmt).scalars().one_or_none()

        if basket_client is None:
            new_basket = BasketClient(client_id=client_id)
            session.add(new_basket)
            session.commit()
            session.refresh(new_basket)
            basket_client = new_basket


        # Проверка на есть ли такой товар в корзине, чтоб не было бага
        stmt = select(BasketProduct).where(and_(BasketProduct.basket_client_id == basket_client.id, BasketProduct.product_id == data.product_id))

        exist = session.execute(stmt).scalars().one_or_none()

        if exist:
            exist.amount += data.amount
        else:
            # Если товара нет, то добавляем новый
            new_item = BasketProduct(amount=data.amount, product_id=data.product_id, basket_client_id=basket_client.id)
            session.add(new_item)
            session.flush()

        session.commit()

    return {"status": True}


# Get и Post запросы для Избранного
# Ручка для перехода на страничку ИЗБРАННОЕ при нажатии кнопки Избранное
@app.get("/favourites", response_class=HTMLResponse)
def homes(request: Request):
    with SessionLocal() as session:
        stmt = (select(Favourites)
                .join(Products, Favourites.product_id == Products.id)
                .options(selectinload(Favourites.product)))  # если есть связь relationship

        favourites = session.execute(stmt).scalars().all()
    return templates.TemplateResponse("favourites.html", {"request": request, "favourites": favourites})


@app.post("/favourites")
def add_to_favourites(request: Request, data: FavCreate):
    user = request.session.get("user")
    if user is None:
        return templates.TemplateResponse("authorization.html", {"request": request})

    client_id = user.get("client_id")
    user = get_current_user(client_id)

    with SessionLocal() as session:
        # Проверяем, есть ли уже такой товар в избранном у этого клиента
        stmt = select(Favourites).where(Favourites.client_id == client_id, Favourites.product_id == data.product_id)
        favourite = session.execute(stmt).scalars().one_or_none()

        # Если нет — добавляем
        if favourite is None:
            stmt = insert(Favourites).values(client_id=client_id, product_id=data.product_id)
            session.execute(stmt)
            session.commit()

    return {"status": True}


# Post запрос данных пользователей
@app.post("/reg")
def homes(request: Request, data: RegCreate):
    with SessionLocal() as session:
        stmt = select(Client).where(or_(Client.email == data.email, Client.phone_number == data.phone_number))
        user_exist = session.execute(stmt).scalars().one_or_none()
        if user_exist is not None:
            return {"status": False}
        stmt = insert(Client).values(first_name=data.first_name, middle_name=data.middle_name, last_name=data.last_name,
                                     email=data.email, password=hash_password(data.password),
                                     phone_number=data.phone_number).returning(Client.id)
        client_id = session.execute(stmt).scalar_one()

        stmt = insert(BasketClient).values(client_id=client_id)
        session.execute(stmt)
        session.commit()
    return {"status": True}


# Работаем с авторизацией
@app.post("/authorization")
def homes(request: Request, data: AuthoCreate):
    with SessionLocal() as session:
        stmt = select(Client).where(or_(Client.email == data.login, Client.phone_number == data.login))
        user_exist = session.execute(stmt).scalars().one_or_none()
        if user_exist is None:
            return {"status": False}

        if not verify_password(data.password, user_exist.password):
            return {"status": False}
        request.session["user"] = {"client_id": user_exist.id}
        return {"status": True, "client_id": user_exist.id}


@app.get("/autho", response_class=HTMLResponse)
def homes(request: Request):
    request.session.clear()
    return templates.TemplateResponse("authorization.html", {"request": request})


@app.get("/personalaccount", response_class=HTMLResponse)
def homes(request: Request):
    user = request.session.get("user")
    if user is None:
        return templates.TemplateResponse("authorization.html", {"request": request})
    client_id = user.get("client_id")
    user = get_current_user(client_id)
    return templates.TemplateResponse("personalaccount.html", {"request": request, "user": user})


def get_current_user(client_id):
    with SessionLocal() as session:
        stmt = select(Client).where(Client.id == client_id)
        client = session.execute(stmt).scalars().first()
        if not client:
            return {"status": False, "message": "Пользователь не найден"}

        return {
            "status": True,
            "first_name": client.first_name,
            "last_name": client.last_name,
            "email": client.email
        }


@app.get("/forgotpassword", response_class=HTMLResponse)
def homes(request: Request):
    request.session.clear()
    return templates.TemplateResponse("forgot_the_password.html", {"request": request})


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_verification_code(receiver_email: str, code: str):
    # данные отправителя (mail.ru)
    sender_email = "ivan_ivanov_ivanovich1234@mail.ru"
    sender_password = os.getenv("EMAILPASSWORD")  # пароль приложения

    # тема и тело письма
    subject = "Код подтверждения"
    body = f"Ваш код подтверждения: {code}"

    # формирование письма
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # подключение к SMTP-серверу mail.ru
        with smtplib.SMTP("smtp.mail.ru", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print(f"✅ Код '{code}' отправлен на {receiver_email}")
            return True
    except Exception as e:
        print(f"❌ Ошибка при отправке: {e}")
        return False


@app.post("/forgotpasswordcode")
def homes(request: Request, data: ForgotCreate):
    with SessionLocal() as session:
        code_6 = str(random.randint(100000, 999999))
        stmt = insert(Forgotpasswordcode).values(email=data.email, code=code_6)
        session.execute(stmt)
        session.commit()

        send_verification_code(data.email, code_6)

    return {"status": "Успешно обновилось"}


@app.post("/forgotpassword/verify/code")
def homes(request: Request, data: VerifyCode):
    with SessionLocal() as session:
        stmt = select(Forgotpasswordcode).where(data.email == Forgotpasswordcode.email).order_by(
            Forgotpasswordcode.id.desc())
        checking = session.execute(stmt).scalars().first()
        if checking.code == data.code:
            return {"status": True, "message": "Код совпадает"}
        else:
            return {"status": False, "message": "Неверный код"}


@app.post("/forgotpassword/password/new")
def homes(request: Request, data: NewPassword):
    with SessionLocal() as session:
        stmt = update(Client).where(Client.email == data.email).values(password=hash_password(data.new_password))
        session.execute(stmt)
        session.commit()
        return {"message": "Пароль успешно изменен"}




@app.get("/myorders", response_class=HTMLResponse)
def homes(request: Request):
    user = request.session.get("user")
    client_id = user.get("client_id")
    with SessionLocal() as session:
        stmt = (select(Order).options(selectinload(Order.orderproduct).selectinload(Orderproduct.product)).where(Order.client_id == client_id))
        orders = session.execute(stmt).scalars().all()

    user_data = get_current_user(client_id)

    return templates.TemplateResponse("my_orders.html",{"request": request, "orders": orders, "user": user_data})




# работа над ПОИСКОМ

@app.get("/search", response_class=HTMLResponse)
def homes(
    request: Request,
    q: str = Query("", description="поисковый запрос"),
    page: int = Query(1, ge=1, description="номер страницы"),
    category : str = Query("", description="категория")
):
    total_in_page = 2
    with SessionLocal() as session:
        stmt = select(Products).join(Category).where(or_(Category.name == category, category == "")).where(Products.name.ilike(f"%{q}%")).offset(total_in_page*(page-1)).limit(total_in_page)
        list_of_products=session.execute(stmt).scalars().all()

        stmt = (select(func.count(Products.id)).join(Category).where(or_(Category.name == category, category == "")).where(Products.name.ilike(f"%{q}%")))
        amount = session.execute(stmt).scalar()

        amount_of_pages = amount // total_in_page

        if amount % total_in_page != 0:
            amount_of_pages += 1

        stmt = select(Category)
        categories = session.execute(stmt).scalars().all()



    return templates.TemplateResponse("search.html",{"request": request, "list_of_products" : list_of_products, "categories" : categories,"category" : category, "page" : page, "q" : q,"amount":amount, "amount_of_pages" : amount_of_pages})


if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # название файла (main.py) и объекта app
        host="0.0.0.0",
        port=8000,
        reload=True
    )

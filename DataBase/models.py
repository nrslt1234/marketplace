from datetime import datetime
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, create_engine, select, insert, delete, update, DateTime, func, Table, Column
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship





class Base(DeclarativeBase):
    pass

class Service(Base):
    __tablename__ = "service"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()


class Ourwork(Base):
    __tablename__ = "ourwork"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    photo: Mapped[str] = mapped_column()



# Модели для проекта
purchases_products = Table(
    "purchases_products",
    Base.metadata,
    Column("purchase_id", ForeignKey("purchases.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True),
)
class Products(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    price: Mapped[int] = mapped_column()
    availability: Mapped[bool] = mapped_column()
    description: Mapped[str] = mapped_column()
    photo: Mapped[str] = mapped_column()
    # created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    purchases: Mapped[List["Purchases"]] = relationship(secondary=purchases_products, back_populates="products")
    basket_products: Mapped[List["BasketProduct"]] = relationship(back_populates="product")
    favourites: Mapped[List["Favourites"]] = relationship(back_populates="product")
    orderproduct: Mapped[List["Orderproduct"]] = relationship(back_populates="product")

    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    category: Mapped["Category"] = relationship(back_populates="products")


class BasketClient(Base):
    __tablename__ = "basket_client"
    id: Mapped[int] = mapped_column(primary_key=True)
    update_at: Mapped[datetime] = mapped_column(DateTime, onupdate=func.now())

    basket_products: Mapped[List["BasketProduct"]] = relationship(back_populates="basket_client")

    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"))
    client: Mapped["Client"] = relationship(back_populates="basket_client")

class BasketProduct(Base):
    __tablename__ = "basket_product"
    id: Mapped[int] = mapped_column(primary_key=True)
    amount:  Mapped[int] = mapped_column()

    basket_client_id: Mapped[int] = mapped_column(ForeignKey("basket_client.id"))
    basket_client: Mapped["BasketClient"] = relationship(back_populates="basket_products")

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    product: Mapped["Products"] = relationship(back_populates="basket_products")


class Order(Base):
    __tablename__ = "order"
    id: Mapped[int] = mapped_column(primary_key=True)

    client_id:  Mapped[int] = mapped_column(ForeignKey("client.id"))
    datetime: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    status: Mapped[str] = mapped_column()

    orderproduct: Mapped[List["Orderproduct"]] = relationship(back_populates="order")


class Orderproduct(Base):
    __tablename__ = "orderproduct"
    id: Mapped[int] = mapped_column(primary_key=True)

    product: Mapped["Products"] = relationship(back_populates="orderproduct")
    order: Mapped["Order"] = relationship(back_populates="orderproduct")
    amount: Mapped[int] = mapped_column()


    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    product_id:  Mapped[int] = mapped_column(ForeignKey("products.id"))




class Client(Base):
    __tablename__ = "client"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column()
    middle_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    wallet: Mapped[int] = mapped_column()
    total_costs: Mapped[int] = mapped_column()
    email: Mapped[str] = mapped_column()
    password:  Mapped[str] = mapped_column()
    phone_number:  Mapped[str] = mapped_column()

    purchases: Mapped[List["Purchases"]] = relationship(back_populates="client")
    basket_client: Mapped["BasketClient"] = relationship(back_populates="client")
    favourites: Mapped[List["Favourites"]] = relationship(back_populates="client")
class Purchases(Base):
    __tablename__ = "purchases"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"))
    client: Mapped["Client"] = relationship(back_populates="purchases")
    products: Mapped[List["Products"]] = relationship(secondary=purchases_products, back_populates="purchases")




class Category(Base):
    __tablename__ = "category"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()


    products: Mapped[List["Products"]] = relationship(back_populates="category")


# Таблица Избранное
class Favourites(Base):
    __tablename__ = "favourites"
    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    product: Mapped["Products"] = relationship(back_populates="favourites")

    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"))
    client: Mapped["Client"] = relationship(back_populates="favourites")


class Forgotpasswordcode(Base):
    __tablename__ = "forgotpasswordcode"
    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column()
    code: Mapped[str] = mapped_column()
    datetime: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())





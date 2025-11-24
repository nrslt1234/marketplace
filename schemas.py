from typing import List

from pydantic import BaseModel, Field

# class ItemBase(BaseModel):
#     title: str = Field(min_length=1, max_length=120)
#     description: str | None = None
#
# class ItemCreate(ItemBase):
#     pass
#
# class ItemUpdate(BaseModel):
#     title: str | None = Field(default=None, min_length=1, max_length=120)
#     description: str | None = None


class BasketBase(BaseModel):
    product_id : int = Field()
    client_id : int = Field()

class BasketCreate(BasketBase):
    amount : int = Field()

class FavBase(BaseModel):
    product_id: int = Field()
    client_id: int = Field()

# Нам ведь не нужно количество, нужно только product_id
# client_id как будто не нужен, так как с избранного переходят в корзину, где как раз важно знать, какой имеено человек покупает товар
class FavCreate(FavBase):
   pass

# Пользовательские данные

class RegBase(BaseModel):
    first_name: str = Field()
    middle_name: str = Field()
    last_name: str = Field()
    email: str = Field()
    password: str = Field()
    phone_number: str = Field()

class RegCreate(RegBase):
   pass


class AuthoBase(BaseModel):
    login: str = Field()
    password: str = Field()

class AuthoCreate(AuthoBase):
   pass


class Forgotpassword(BaseModel):
    email: str = Field()


class ForgotCreate(Forgotpassword):
   pass


# Для проверки код по email
class VerifyCode(BaseModel):
    email: str = Field()
    code: str = Field(min_length=6, max_length=6)

class VerifyCreate(VerifyCode):
    pass


class NewPassword(BaseModel):
    email: str = Field()

    new_password: str = Field()


class NewCreate(NewPassword):
    pass


class Newamount(BaseModel):
    amount: int = Field()
    product_id: int = Field()

class NewamountCreate(Newamount):
    pass



class CheckItem(BaseModel):

    amount: int = Field()
    product_id: int = Field()

class OrderSchema(BaseModel):
    items: List[CheckItem] = Field()

class CheckItemCreate(BaseModel):
    pass
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
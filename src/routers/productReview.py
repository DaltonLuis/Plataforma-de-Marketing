from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List
from shared.security import get_session
from ..utils.models import Post, Order, Product, PostBase, ProductBase, OrderBase

router = APIRouter(prefix='/api')


##############Post#####################

# Rota para obter todos os posts de um produto específico
@router.get("/see/posts/product/{product_id}")
def get_posts_by_product(product_id: int, session: Session = Depends(get_session)):
    posts = session.exec(select(Post).where(Post.productId == product_id)).all()
    return posts

# Rota para obter todos os posts de um vendedor específico
@router.get("/see/posts/seller/{seller_id}")
def get_posts_by_seller(seller_id: int, session: Session = Depends(get_session)):
    posts = session.exec(select(Post).where(Post.sellerId == seller_id)).all()
    return posts

# Rota para atualizar um post de produto existente
@router.put("/update/post/{post_id}")
def update_post(post_id: int, post_update: PostBase, session: Session = Depends(get_session)):
    db_post = session.get(Post, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    for key, value in post_update.dict(exclude_unset=True).items():
        setattr(db_post, key, value)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


# Rota para excluir um post de produto existente
@router.delete("/delete/post/{post_id}")
def delete_post(post_id: int, session: Session = Depends(get_session)):
    db_post = session.get(Post, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    session.delete(db_post)
    session.commit()
    return {"message": "Post deleted successfully"}

# Endpoint para lidar com posts de produtos
@router.post("/add/posts/")
def create_post(post: PostBase, session: Session = Depends(get_session)):
    db_post = Post(**post.dict())
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


##############Product######################


# Rota para criar um novo produto
@router.post("/add/products/")
def create_product(product: ProductBase, session: Session = Depends(get_session)):
        db_product = Product(**product.dict())
        session.add(db_product)
        session.commit()
        session.refresh(db_product)
        return db_product

# Rota para listar todos os produtos de um vendedor (seller)
@router.get("/see/product/{seller_id}")
def list_products_by_seller(seller_id: int, session: Session = Depends(get_session)):
    products = session.exec(select(Product).where(Product.sellerId == seller_id)).all()
    return products
    

#################Order###################

# Rota para obter detalhes de um pedido específico
@router.get("/see/orders/{order_id}")
def get_order_details(order_id: int, session: Session = Depends(get_session)):
    db_order = session.get(Order, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

# Rota para criar um novo pedido de produto
@router.post("/add/orders")
def create_order(order: OrderBase, session: Session = Depends(get_session)):
    db_order = Order(**order.dict())
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    return db_order

# Rota para excluir um pedido de produto existente
@router.delete("/delete/orders/{order_id}")
def delete_order(order_id: int, session: Session = Depends(get_session)):
    db_order = session.get(Order, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    session.delete(db_order)
    session.commit()
    return {"message": "Order deleted successfully"}

# Rota para obter todos os pedidos de um comprador específico
@router.get("/see/orders/buyer/{buyer_id}")
def get_orders_by_buyer(buyer_id: int, session: Session = Depends(get_session)):
    orders = session.exec(select(Order).where(Order.buyerId == buyer_id)).all()
    return orders

# Rota para atualizar um pedido de produto existente
@router.put("/update/orders/{order_id}")
def update_order(order_id: int, order_update: OrderBase, session: Session = Depends(get_session)):
    db_order = session.get(Order, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    for key, value in order_update.dict(exclude_unset=True).items():
        setattr(db_order, key, value)
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    return db_order
from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy import Index, UniqueConstraint
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import EmailStr, field_validator

##############Base#################

class PostBase(SQLModel):
    sellerId: Optional[int] = Field(foreign_key="user.userId", ondelete="CASCADE")
    productId: Optional[int] = Field(foreign_key="product.productId", ondelete="CASCADE")

class Country(SQLModel, table=True):
    __tablename__ = "country"
    __table_args__ = (
        UniqueConstraint('countryName', name='uq_country_name'),
        Index('idx_country_name', 'countryName'),
    )
    
    countryId: Optional[int] = Field(default=None, primary_key=True)
    countryName: str = Field(nullable=False, max_length=100)
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    addresses: List["Address"] = Relationship(back_populates="countries")

class AddressBase(SQLModel):
    distrit: Optional[str] = Field(max_length=100)

class CategoryBase(SQLModel):
    categoryName: Optional[str] = Field(max_length=100)

class OrderBase(SQLModel):
    itemQuantity: Optional[str] = Field(max_length=50)
    invoiceAmount: Optional[float] = None
    transactStatus: Optional[str] = Field(max_length=50)
    paymentDate: Optional[datetime] = None
    buyerId: Optional[int] = Field(foreign_key="user.userId", ondelete="CASCADE")
    productId: Optional[int] = Field(foreign_key="product.productId", ondelete="CASCADE")

class ProductBase(SQLModel):
    productName: str = Field(nullable=False, max_length=200)
    productDescription: Optional[str] = Field(max_length=1000)
    quantity: Optional[int] = Field(ge=0)
    unitPrice: Optional[float] = Field(ge=0)
    unitInStock: Optional[int] = Field(ge=0)
    unitInOrder: Optional[int] = Field(ge=0, default=0)
    picture: Optional[str] = Field(max_length=500)
    categoryId: int = Field(foreign_key="category.categoryId", ondelete="RESTRICT")

class ProductReviewBase(SQLModel):
    productId: Optional[int] = Field(foreign_key="product.productId", ondelete="CASCADE")
    customerReview: Optional[int] = None
    customerId: Optional[int] = Field(foreign_key="user.userId", ondelete="CASCADE")
    rating: Optional[int] = Field(ge=1, le=5)

class UserBase(SQLModel):
    userFirstName: str = Field(nullable=False, max_length=100)
    userLastName: str = Field(nullable=False, max_length=100)
    userEmail: str = Field(nullable=False, max_length=255)
    userType: str = Field(nullable=False, max_length=20)
    password: str = Field(nullable=False, max_length=255)
    userGender: Optional[str] = Field(max_length=20)
    userPhoneNumber: Optional[str] = Field(max_length=20)
    userImage: Optional[str] = Field(max_length=500)
    companyName: Optional[str] = Field(max_length=200)
    dateOfBirth: Optional[str] = Field(max_length=50)
    description: Optional[str] = Field(max_length=1000)
    adressId: Optional[int] = Field(default=None, foreign_key="address.adressId", ondelete="SET NULL")
    categoryId: Optional[int] = Field(default=None, foreign_key="category.categoryId", ondelete="SET NULL")

class VerificationCodeBase(SQLModel):
    userEmail: str = Field(nullable=False, max_length=255)
    code: int = Field(ge=0, le=9999)

class CommentBase(SQLModel):
    userId: Optional[int] = Field(default=None, foreign_key="user.userId", ondelete="CASCADE")
    commentDescription: Optional[str] = Field(max_length=2000)

class CommentReplyBase(SQLModel):
    userId: Optional[int] = Field(default=None, foreign_key="user.userId", ondelete="CASCADE")
    commentDescription: Optional[str] = Field(max_length=2000)

##############Model#################

class Post(PostBase, table=True):
    __tablename__ = "post"
    __table_args__ = (
        Index('idx_post_seller', 'sellerId'),
        Index('idx_post_product', 'productId'),
    )
    
    postId: Optional[int] = Field(default=None, primary_key=True)
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    author: Optional["User"] = Relationship(back_populates="posts")
    product: Optional["Product"] = Relationship(back_populates="posts")

class Address(AddressBase, table=True):
    __tablename__ = "address"
    __table_args__ = (
        Index('idx_address_country', 'countryId'),
        Index('idx_address_distrit', 'distrit'),
    )
    
    adressId: Optional[int] = Field(default=None, primary_key=True)
    countryId: int = Field(foreign_key="country.countryId", ondelete="RESTRICT")
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    users: List["User"] = Relationship(back_populates="address")
    countries: Optional["Country"] = Relationship(back_populates="addresses")
    

class Category(CategoryBase, table=True):
    __tablename__ = "category"
    __table_args__ = (
        UniqueConstraint('categoryName', name='uq_category_name'),
        Index('idx_category_name', 'categoryName'),
    )
    
    categoryId: Optional[int] = Field(default=None, primary_key=True)
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    users: List["User"] = Relationship(back_populates="category")
    products: List["Product"] = Relationship(back_populates="category")

class Order(OrderBase, table=True):
    __tablename__ = "order"
    __table_args__ = (
        Index('idx_order_buyer', 'buyerId'),
        Index('idx_order_product', 'productId'),
        Index('idx_order_date', 'orderDate'),
    )
    
    orderId: Optional[int] = Field(default=None, primary_key=True)
    orderDate: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    person: Optional["User"] = Relationship(back_populates="orders")
    product: Optional["Product"] = Relationship(back_populates="orders")

class Product(ProductBase, table=True):
    __tablename__ = "product"
    __table_args__ = (
        Index('idx_product_category', 'categoryId'),
        Index('idx_product_name', 'productName'),
    )
    
    productId: Optional[int] = Field(default=None, primary_key=True)
    disabled: bool = Field(default=False)
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    category: Optional["Category"] = Relationship(back_populates="products")
    posts: List["Post"] = Relationship(back_populates="product")
    productReview: List["ProductReview"] = Relationship(back_populates="product")
    orders: List["Order"] = Relationship(back_populates="product")

class SellerReview(SQLModel, table=True):
    __tablename__ = "sellerreview"
    __table_args__ = (
        Index('idx_seller_review_seller', 'sellerId'),
        Index('idx_seller_review_customer', 'customerId'),
    )
    
    sellerReviewId: Optional[int] = Field(default=None, primary_key=True)
    sellerId: Optional[int] = Field(foreign_key="user.userId", ondelete="CASCADE")
    customerReview: Optional[str] = Field(max_length=2000)
    customerId: Optional[int] = Field(foreign_key="user.userId", ondelete="CASCADE")
    rating: Optional[int] = Field(ge=1, le=5)
    hasRating: Optional[bool] = Field(default=False)
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProductReview(ProductReviewBase, table=True):
    __tablename__ = "productreview"
    __table_args__ = (
        Index('idx_product_review_product', 'productId'),
        Index('idx_product_review_customer', 'customerId'),
    )
    
    productReviewId: Optional[int] = Field(default=None, primary_key=True)
    hasRating: bool = Field(default=False)
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    product: Optional[Product] = Relationship(back_populates="productReview")
    person: Optional["User"] = Relationship(back_populates="productReview")

class User(UserBase, table=True):
    __tablename__ = "user"
    __table_args__ = (
        UniqueConstraint('userEmail', name='uq_user_email'),
        Index('idx_user_email', 'userEmail'),
        Index('idx_user_type', 'userType'),
        Index('idx_user_address', 'adressId'),
    )
    
    userId: Optional[int] = Field(default=None, primary_key=True)
    disabled: bool = Field(default=False)
    accessToken: Optional[str] = Field(max_length=500)
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    address: Optional["Address"] = Relationship(back_populates="users")
    category: Optional["Category"] = Relationship(back_populates="users")
    posts: List["Post"] = Relationship(back_populates="author")
    productReview: List["ProductReview"] = Relationship(back_populates="person")
    comments: List["Comment"] = Relationship(back_populates="user")
    commentsRpl: List["CommentReply"] = Relationship(back_populates="user")
    orders: List["Order"] = Relationship(back_populates="person")


class VerificationCode(VerificationCodeBase, table=True):
    __tablename__ = "verificationcode"
    __table_args__ = (
        Index('idx_verification_email', 'userEmail'),
        Index('idx_verification_expiration', 'expirationTime'),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    expirationTime: datetime = Field(nullable=False)
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Comment(CommentBase, table=True):
    __tablename__ = "comment"
    __table_args__ = (
        Index('idx_comment_user', 'userId'),
        Index('idx_comment_created', 'createdAt'),
    )
    
    commentId: Optional[int] = Field(default=None, primary_key=True)
    totalLikes: Optional[int] = Field(default=0, ge=0)
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: Optional["User"] = Relationship(back_populates="comments")
    commentReplies: List["CommentReply"] = Relationship(back_populates="comment")

class CommentReply(CommentReplyBase, table=True):
    __tablename__ = "commentreply"
    __table_args__ = (
        Index('idx_comment_reply_user', 'userId'),
        Index('idx_comment_reply_comment', 'commentId'),
    )
    
    commentReplyId: Optional[int] = Field(default=None, primary_key=True)
    commentId: Optional[int] = Field(default=None, foreign_key="comment.commentId", ondelete="CASCADE")
    totalLikes: Optional[int] = Field(default=0, ge=0)
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: Optional["User"] = Relationship(back_populates="commentsRpl")
    comment: Optional["Comment"] = Relationship(back_populates="commentReplies")

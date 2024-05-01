from sqlalchemy import create_engine
from sqlalchemy import DateTime
from sqlalchemy import Column, Integer,Double, Sequence, String, Text, PrimaryKeyConstraint, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy import and_
from datetime import datetime
from datetime import timedelta
from pydantic import BaseModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import os
# import schedule

LOGIN = os.environ.get("login_db_odin_doma")
PASSWORD = os.environ.get("password_db_odin_doma")
SERVER = os.environ.get("server_db_odin_doma")
NAME_DB = os.environ.get("name_db_odin_doma")

Base = declarative_base()
connection_string = f"mysql+pymysql://{LOGIN}:{PASSWORD}@{SERVER}/{NAME_DB}"
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)

class DayWeeklyInDB(Base):
    __tablename__ = "day_weekly"
    id_weekly = Column(Integer)
    name_day_weekly = Column(String(15))
    short_name = Column(String(5))
    order_weekly = Column(Integer)
    day_number = Column(Integer)
    __table_args__ = (PrimaryKeyConstraint(id_weekly), {},)

class CategoryInDB(Base):
    __tablename__ = "category"
    id_category = Column(Integer)
    name_category = Column(String(30))
    order_category = Column(Integer)
    __table_args__ = (PrimaryKeyConstraint(id_category), {},)

class DishInDB(Base):
    __tablename__ = "dish"
    id_dish = Column(Integer)
    name_dish = Column(String(50))
    description_dish = Column(String(200))
    id_category = Column(Integer,ForeignKey('category.id_category'))
    category = relationship("CategoryInDB")
    price = Column(Integer)
    ccal = Column(Integer)
    proteins = Column(Integer)
    fats = Column(Integer)
    carbohydrates = Column(Integer)
    weight = Column(Integer)
    composition = Column(String(200))
    photo = Column(String(250))
    __table_args__ = (PrimaryKeyConstraint(id_dish), {},)

class TimetableInDB(Base):
    __tablename__ = "time_table"
    id_weekly = Column(Integer,ForeignKey('day_weekly.id_weekly',name='fk_weekly_1'))
    weekly = relationship("DayWeeklyInDB",foreign_keys=[id_weekly])
    id_dish = Column(Integer,ForeignKey('dish.id_dish',name='fk_dish_1'))
    dish = relationship("DishInDB",foreign_keys=[id_dish])
    __table_args__ = (PrimaryKeyConstraint(id_weekly,id_dish), {},)

class ShoppingCartInDB(Base):
    __tablename__ = "shoping_cart"
    id = Column(Integer)
    id_user = Column(Integer,nullable=False)
    id_dish = Column(Integer,ForeignKey('dish.id_dish'),nullable=False)
    dish = relationship("DishInDB")
    quantity = Column(Integer,nullable=False)
    __table_args__ = (PrimaryKeyConstraint(id), {},)

class OrderPositionInDB(Base):
    __tablename__ = "order_position"
    id_order = Column(Integer,nullable=False)
    id_dish = Column(Integer,nullable=False)
    quantity = Column(Integer,nullable=False)
    __table_args__ = (PrimaryKeyConstraint(id_order,id_dish), {},)


class PaymentMethodInDB(Base):
    __tablename__ = "payment"
    id = Column(Integer)
    method_name = Column(String(12),nullable=False)
    actual = Column(Boolean,nullable=False)
    __table_args__ = (PrimaryKeyConstraint(id), {},)

class InfoOrderInDB(Base):
    __tablename__ = "order"
    id = Column(Integer)
    address = Column(String(200),nullable=False)
    quantity_person = Column(Integer,nullable=False)
    delivery_time = Column(String(20),nullable=False)
    cutlery = Column(Boolean,nullable=False)
    payment_id = Column(Integer, ForeignKey('payment.id'),nullable=False)
    payment = relationship('PaymentMethodInDB')
    number_phone = Column(String(20),nullable=False)
    promocode = Column(String(50),nullable=False)
    wishes = Column(String(250),nullable=False) 
    price = Column(Integer,nullable=False)
    id_user = Column(Integer,nullable=False)
    order_time = Column(DateTime,nullable=False)
    __table_args__ = (PrimaryKeyConstraint(id), {},)

class StatusOrderInDB(Base):
    __tablename__ = "order_status"
    id = Column(Integer)
    status_name = Column(String(50),nullable=False,unique=True)
    order_status = Column(Integer,nullable=True)
    __table_args__ = (PrimaryKeyConstraint(id), {},)

class HistoryStatusInDB(Base):
    __tablename__ = "order_history"
    id_order = Column(Integer,ForeignKey('order.id',name='fk_order_history_order'))
    order = relationship('InfoOrderInDB',foreign_keys=[id_order])
    id_status = Column(Integer,ForeignKey('order_status.id',name='fk_order_history_order_status'))
    status = relationship('StatusOrderInDB',foreign_keys=[id_status])
    date = Column(DateTime,nullable=False)
    __table_args__ = (PrimaryKeyConstraint(id_order,id_status,date), {},)

class UsersInDB(Base):
    __tablename__ = "users"
    id = Column(Integer)
    login = Column(String(30),unique=True,nullable=False)
    password = Column(String(250),nullable=False)
    is_admin = Column(Boolean,nullable=False)
    __table_args__ = (PrimaryKeyConstraint(id), {},)

class TokenInDB(Base):
    __tablename__ = "token"
    id_user = Column(Integer, ForeignKey('users.id'),nullable=False)
    user = relationship('UsersInDB')
    token = Column(String(100), nullable=False, unique=True)
    __table_args__ = (PrimaryKeyConstraint(id_user), {},)

Base.metadata.create_all(engine)
 
def clean_table():
    with Session() as session:
        result = session.query(ShoppingCartInDB).delete()
        session.commit()
    return result
    
# schedule.every().day.at("16:48").do(clean_table)
# while True:
#     schedule.run_pending()
#     time.sleep(1)
from pydantic import BaseModel
from typing import Optional
from typing import List
from pydantic import Field
from odin_doma_db_model import*
from odin_doma_baseModel import*


class Dish(BaseModel):
    id_dish: Optional[int] = Field(None)
    name_dish: str
    description_dish: str
    price: int
    ccal: int
    proteins: int
    fats: int
    carbohydrates: int
    weight: int
    composition: str
    photo: str
    id_category: int
    weekly_day_list: List[int]

class RequestAddDish(BaseModel):
    dish:Dish

class ResponseAddDish(BaseModel):
    success:bool
    error:str
    dish:Dish

def dish_model_to_model_db(model:Dish):
    dish = DishInDB()
    dish.name_dish = model.name_dish
    dish.description_dish = model.description_dish
    dish.price = model.price
    dish.ccal = model.ccal
    dish.proteins = model.proteins
    dish.fats = model.fats
    dish.carbohydrates = model.carbohydrates
    dish.weight = model.weight
    dish.composition = model.composition
    dish.photo = model.photo
    dish.id_category = model.id_category
    return dish

def dish_model_db_to_model(model_db:DishInDB,weekly_day_list = []):
    dish = Dish(id_dish= model_db.id_dish,
        name_dish = model_db.name_dish,
        description_dish = model_db.description_dish,
        price = model_db.price,
        ccal = model_db.ccal,
        proteins = model_db.proteins,
        fats = model_db.fats,
        carbohydrates = model_db.carbohydrates,
        weight = model_db.weight,
        composition = model_db.composition,
        photo = model_db.photo,
        id_category = model_db.id_category,
        weekly_day_list=weekly_day_list)
    
    return dish

class InfoOrder(BaseModel):
    address: str
    quantity_person: int
    delivery_time: str
    cutlery: bool
    payment_id: int
    number_phone: str
    promocode: str
    wishes: str
    price: int
    id_user: int

class FullInfoOrder(BaseModel):
    id_order: int 
    address: str
    quantity_person: int
    delivery_time: str
    cutlery: bool
    payment: PaymentMethod
    number_phone: str
    promocode: str
    wishes: str
    price: int
    id_user: int
    order_time: datetime
    dish_list: List[OrderPositionShort]
    last_status: Status
    

class HistoryStatus(BaseModel):
    id_order: int
    id_status: int
    date: Optional[datetime] = Field(None)

class RequestHistoryStatus(BaseModel):
    item: HistoryStatus   

class RequestAddInfo(BaseModel):
    info:InfoOrder

def history_order_model_to_model_db(model:HistoryStatus):
    history = HistoryStatusInDB()
    history.id_order = model.id_order
    history.id_status = model.id_status
    history.date = datetime.now()

    return history

def info_model_to_model_db(model:InfoOrder):
    info = InfoOrderInDB()
    info.address = model.address
    info.quantity_person = model.quantity_person
    info.delivery_time = model.delivery_time
    info.cutlery = model.cutlery
    info.payment_id = model.payment_id
    info.number_phone = model.number_phone
    info.promocode = model.promocode
    info.wishes = model.wishes
    info.price = model.price
    info.id_user = model.id_user
    info.order_time = datetime.now()

    return info

def info_model_db_to_model(model_db:InfoOrderInDB):
    info = InfoOrder(
        address = model_db.address,
        quantity_person = model_db.quantity_person,
        delivery_time = model_db.delivery_time,
        cutlery = model_db.cutlery,
        payment_id = model_db.payment_id,
        number_phone = model_db.number_phone,
        promocode = model_db.promocode,
        wishes = model_db.wishes,
        price = model_db.price,
        id_user = model_db.id_user,
        order_time = model_db.order_time)
       
    return info

def info_order_model(order_model):
    info = InfoOrder(
        address = order_model.address,
        quantity_person = order_model.quantity_person,
        delivery_time = order_model.delivery_time,
        cutlery = order_model.cutlery,
        payment_id = order_model.payment_id,
        number_phone = order_model.number_phone,
        promocode = order_model.promocode,
        wishes = order_model.wishes,
        price = order_model.price,
        id_user = order_model.id_user,
       )
    
    return info

def order_position_db_to_order_position_short(position:OrderPositionInDB):
    with Session() as session:
        dish = session.query(DishInDB).filter(DishInDB.id_dish == position.id_dish).first()
        name_dish = "Нет блюда"
        if dish:
            name_dish = dish.name_dish

        return OrderPositionShort(id_dish=position.id_dish, name_dish=name_dish, quantity=position.quantity)

# def last_status_order_db(status:InfoOrderInDB):
#     with Session() as session:
#         current_order = (session.query(HistoryStatusInDB).
#                         filter(HistoryStatusInDB.id_order == status.id).order_by(HistoryStatusInDB.date.desc()).first())
#         status_name = 'Нет статуса'
#         if current_order:
#             status_name = current_order.status.status_name
            
#         return Status(id=current_order.status.id,status_name=status_name)

def info_fullorder_model(order_model:InfoOrderInDB):
    with Session() as session:
        payment = order_model.payment
        paymentMethod = PaymentMethod(id=payment.id,method_name=payment.method_name)
        position_list = session.query(OrderPositionInDB).filter(OrderPositionInDB.id_order == order_model.id).all()
        position_short_list = []

        for i in position_list:
            position =order_position_db_to_order_position_short(i)
            position_short_list.append(position)
        
        last_status = (session.query(HistoryStatusInDB).
                filter(HistoryStatusInDB.id_order == order_model.id).order_by(HistoryStatusInDB.date.desc()).first())
        status_name = 'Нет статуса'
        if last_status:
            status_name = last_status.status.status_name
            
        status = Status(status_name=status_name)

        info = FullInfoOrder(
            id_order = order_model.id,
            address = order_model.address,
            quantity_person = order_model.quantity_person,
            delivery_time = order_model.delivery_time,
            cutlery = order_model.cutlery,
            payment = paymentMethod,
            number_phone = order_model.number_phone,
            promocode = order_model.promocode,
            wishes = order_model.wishes,
            price = order_model.price,
            id_user = order_model.id_user,
            order_time = order_model.order_time,
            dish_list = position_short_list,
            last_status = status)
    
    return info


class ResponseAddInfoOrder(BaseModel):
    success:bool
    error:str
    order:InfoOrder
    positions: List[AddOrderPosition]
    status:Status

class ResponceFullInfoOrder(BaseModel):
    success:bool
    error:str
    order_list:List[FullInfoOrder]
    total: int
    limit: int
    offset: int
    
class ResponceHistoryStatus(BaseModel):
    success:bool
    error:str
    history:HistoryStatus
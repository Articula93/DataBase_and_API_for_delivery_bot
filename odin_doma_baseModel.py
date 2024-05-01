from pydantic import BaseModel
from typing import Optional
from typing import List
from pydantic import Field
from odin_doma_db_model import*


class PaymentMethod(BaseModel):
    id: int
    method_name: str

class OrderPositionShort(BaseModel):
    id_dish: int
    name_dish: str
    quantity: int

class WeeklyDay(BaseModel):
    id: int
    name: str
    short_name: str

class CreateCategory(BaseModel):
    id: int
    name: str

class CreateStatusList(BaseModel):
    id: int
    status_name: str
    order_status: int

class DishDayWeekly(BaseModel):
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

class DishInfoList(BaseModel):
    id_dish: Optional[int] = Field(None)
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

class CategoryInfoList(BaseModel):
    id_dish: Optional[int] = Field(None)
    description_dish: str
    price: int
    ccal: int
    proteins: int
    fats: int
    carbohydrates: int
    weight: int
    composition: str
    photo: str

class CountDishAndQuantityCart(BaseModel):
    id_dish: int
    quantity: int

class DishCartShoping(BaseModel):
    id_user: int
    item: List[CountDishAndQuantityCart]

class InfoCartShopingUser(BaseModel):
    id_dish: int
    quantity: int

class AddOrderPosition(BaseModel):
    id_order: int
    id_dish: int
    quantity: int

class StatusOrder(BaseModel):
    status_name: str
    order_status: int

class Status(BaseModel):
    status_name: str    

class ReplacementStatus(BaseModel):
    id_status: int
    name_status: str

def create_weekly_day_in_db_to_weekly(weekly_day_in_db):
    days = WeeklyDay(id=weekly_day_in_db.id_weekly, 
                    name=weekly_day_in_db.name_day_weekly,
                    short_name=weekly_day_in_db.short_name)
    return days

def create_category_in_db_category(category_in_db):
    category = CreateCategory(id=category_in_db.id_category, name=category_in_db.name_category)
    return category

def create_status_list_in_db_order_status(create_status_list):
    status_list = CreateStatusList(id=create_status_list.id, status_name=create_status_list.status_name,order_status=create_status_list.order_status)
    return status_list

def dish_list_day_weekly_in_db(create_dish_list_in_db):
    dish_list = DishDayWeekly(id_dish=create_dish_list_in_db.id_dish,
                              name_dish=create_dish_list_in_db.name_dish,
                              description_dish=create_dish_list_in_db.description_dish,
                              price=create_dish_list_in_db.price,
                              ccal=create_dish_list_in_db.ccal,
                              proteins=create_dish_list_in_db.proteins,
                              fats=create_dish_list_in_db.fats,
                              carbohydrates=create_dish_list_in_db.carbohydrates,
                              weight=create_dish_list_in_db.weight,
                              composition=create_dish_list_in_db.composition,
                              photo=create_dish_list_in_db.photo,
                              id_category=create_dish_list_in_db.id_category)
    return dish_list

def dish_info_from_db(dish_info_db):
    dish_info = DishInfoList(id_dish=dish_info_db.id_dish,
                              description_dish=dish_info_db.description_dish,
                              price=dish_info_db.price,
                              ccal=dish_info_db.ccal,
                              proteins=dish_info_db.proteins,
                              fats=dish_info_db.fats,
                              carbohydrates=dish_info_db.carbohydrates,
                              weight=dish_info_db.weight,
                              composition=dish_info_db.composition,
                              photo=dish_info_db.photo,
                              id_category=dish_info_db.id_category)
    return dish_info

def category_info_from_db(category_info_db):
    category_info = CategoryInfoList(id_dish = category_info_db.id_dish,
                              description_dish=category_info_db.description_dish,
                              price=category_info_db.price,
                              ccal=category_info_db.ccal,
                              proteins=category_info_db.proteins,
                              fats=category_info_db.fats,
                              carbohydrates=category_info_db.carbohydrates,
                              weight=category_info_db.weight,
                              composition=category_info_db.composition,
                              photo=category_info_db.photo,
                              id_category = category_info_db.id_category)
    return category_info

def cart_info_in_db(cart_info_db):
    cart_info_user = InfoCartShopingUser(id_dish=cart_info_db.id_dish,
                                         quantity=cart_info_db.quantity)
    return cart_info_user

def status_order_in_db(status_order_db):
    status_order = StatusOrder(status_name=status_order_db.status_name,
                               order_status=status_order_db.order_status)
    return status_order

def search_status_upon_order_in_db(status_upon_order_db):
    search_status = Status(id=status_upon_order_db.id,
                                 status_name=status_upon_order_db.status_name)
    return search_status

class RequestInfoDish(BaseModel):
    name_dish: str

class RequestAddCart(BaseModel):
    id_user: int
    item: List[CountDishAndQuantityCart]

class RequestAddOrderPosition(BaseModel):
    id_dish: int
    quantity: int

class RequestReplacementStatus(BaseModel):
    id_status: int

class ResponceAddOrderPosition(BaseModel):
    success: bool
    error: str | None
    positions: List[AddOrderPosition]

class ResponceInfoDish(BaseModel):
    success: bool
    error: str | None
    items: DishInfoList

class ResponceListWeeeklyDay(BaseModel):
    success: bool
    error: str | None
    items: List[WeeklyDay]

class ResponceListCategory(BaseModel):
    success: bool
    error: str | None
    items: List[CreateCategory]

class ResponceStatusList(BaseModel):
    success: bool
    error: str | None
    items: List[CreateStatusList]

class ResponceListDishDayWeekly(BaseModel):
    success: bool
    error: str | None
    items: List[DishDayWeekly]
    
class ResponceInfoCategory(BaseModel):
    success: bool
    error: str | None
    items: List[CategoryInfoList]

class ResponceAddCart(BaseModel):
    success: bool
    error: str | None
    items: DishCartShoping

class ResponceInfoCartShoping(BaseModel):
    success: bool
    error: str | None
    items: List[InfoCartShopingUser]

class ResponceStatusOrder(BaseModel):
    success: bool
    error: str | None
    items: List[StatusOrder]

class ResponceSearchStatus(BaseModel):
    success: bool
    error: str | None
    items: List[Status]

class ResponceReplacementStatus(BaseModel):
    success: bool
    error: str | None
    status: ReplacementStatus





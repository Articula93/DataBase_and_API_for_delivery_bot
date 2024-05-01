from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI, Body, status, Response
from typing import Annotated
from fastapi import Form
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse, FileResponse
from odin_doma_baseModel import *
from odin_doma_db_model import *
import hashlib
from odin_doma_weekly_day import*
from odin_doma_category import*
from odin_doma_status_order import *
from odin_doma_model import*
from utils import *
from odin_doma_admin_model import*
import secrets
print('test')

insert_default_weekly_day()
insert_default_category()
insert_default_status()

app = FastAPI()


@app.get("/")
def response_html():
    return FileResponse("adminka.html")

@app.post("/add_dish")
async def add_dish(req:RequestAddDish):
    with Session() as session:
        add_dish = session.query(DishInDB).filter(DishInDB.name_dish == req.dish.name_dish).first()
        if add_dish:
            return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content={"error": "Блюдо с таким именем уже есть"})
        
        category = session.query(CategoryInDB).filter(CategoryInDB.id_category == req.dish.id_category).first()
        if not category:
            return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content={"error": "Неверный id категории"})

        results= session.query(DayWeeklyInDB.id_weekly).filter(DayWeeklyInDB.id_weekly.in_(req.dish.weekly_day_list))
        results = set(map(lambda t: t[0],results))
        print(results)
        incorrect_id = set(req.dish.weekly_day_list) - results
        print(incorrect_id)        
        if len(incorrect_id) > 0:
            return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content={"error": f"Неверный id дней недели {incorrect_id}"})
        new_dish = dish_model_to_model_db(req.dish)

        session.add(new_dish)
        session.commit()

        for day_id in req.dish.weekly_day_list:
            time_table = TimetableInDB()
            time_table.id_dish = new_dish.id_dish
            time_table.id_weekly = day_id
            session.add(time_table)
        session.commit()

        return ResponseAddDish(success = True,error="", dish = dish_model_db_to_model(new_dish,req.dish.weekly_day_list))

@app.post("/list_dish")
def list_dish(id: int):
    with Session() as session:
        weekly_day = session.query(DayWeeklyInDB).filter(DayWeeklyInDB.id_weekly == id).first()
        if not weekly_day:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, 
                content={"message": "Дня недели с таким id не существует"})
        weekly_day = session.query(DishInDB).filter(TimetableInDB.id_weekly == id).all()
        if not weekly_day:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, 
                content={"message": "Такого id не существует"})
        list_dish = []
        for i in weekly_day:
                list_dish.append(dish_list_day_weekly_in_db(i))
        session.commit()
        return ResponceListDishDayWeekly(success = True,error="",items=list_dish)


@app.get("/list_weekly")
def list_days_weekly():
     with Session() as session:
        list_weekly_in_db = session.query(DayWeeklyInDB).all()
        list_weekly = []
        for i in list_weekly_in_db:
                list_weekly.append(create_weekly_day_in_db_to_weekly(i))
        return ResponceListWeeeklyDay(success=True, error= None, items=list_weekly)
     
     
@app.get("/list_category")
def list_category():
     with Session() as session:
        list_category_in_db = session.query(CategoryInDB).all()
        list_category_dish = []
        for i in list_category_in_db:
                list_category_dish.append(create_category_in_db_category(i))
        return ResponceListCategory(success=True, error= None, items=list_category_dish)
     
     
@app.post("/delete_dish")
def delete_dish(id: int):
    with Session() as session:
            session.query(TimetableInDB).filter(TimetableInDB.id_dish == id).delete()
            delete_dish = session.query(DishInDB).filter(DishInDB.id_dish == id).delete()
            session.commit()
    if not delete_dish:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content={"message": "Блюдо не найдено"})   
    else:
        return JSONResponse(
                status_code=status.HTTP_201_CREATED, 
                content={"message": "Блюдо успешно удалено"})

# @app.post("/info_dish")
# def info_dish(name_dish:str):
#     with Session() as session:
#         results = session.query(DishInDB).filter(DishInDB.name_dish == name_dish).first()
#         if not results:
#             return JSONResponse(
#             status_code=status.HTTP_404_NOT_FOUND, 
#             content={"message": "Блюдо не найдено"})
#         return ResponceInfoDish(success=True, error= None, items=dish_info_from_db(results))
        
@app.get("/info_dish")
def info_dish(req:RequestInfoDish):
    with Session() as session:
        search_dish = session.query(DishInDB).filter(DishInDB.name_dish == req.name_dish).first()
        if not search_dish:
            return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content={"message": "Блюдо не найдено"})
        return ResponceInfoDish(success=True, error= None, items=dish_info_from_db(search_dish))

@app.get("/info_category/{id_category}")
def info_category(id_category: int):
    with Session() as session:
        now = datetime.now()
        day_data = datetime.weekday(now)
        search_category = session.query(DishInDB).join(TimetableInDB,DishInDB.id_dish == TimetableInDB.id_dish).filter(
            DishInDB.id_category == id_category).filter(
            DayWeeklyInDB.day_number == day_data).all()
        
        if not search_category:                      
            return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content={"message": "категория не найдена"})
        list_dish = []
        for i in search_category:
            list_dish.append(category_info_from_db(i))
        return ResponceInfoCategory(success=True, error= None, items=list_dish)

@app.post("/add_cart")
def add_cart_dish(req:RequestAddCart):
    dish_quantity_value = []
    with Session() as session:
        for dish in req.item:
            search_id_dish = session.query(DishInDB).filter(DishInDB.id_dish == dish.id_dish).first()
            if not search_id_dish:
                return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, 
                content={"error": "Неверный id блюда"})
            result_quantity = session.query(ShoppingCartInDB).filter(ShoppingCartInDB.id_dish == dish.id_dish).filter(
            ShoppingCartInDB.id_user == req.id_user).first()
            if result_quantity:
                result_quantity.quantity += dish.quantity
            else:
                data = ShoppingCartInDB()
                data.id_user = req.id_user
                data.id_dish = dish.id_dish
                data.quantity = dish.quantity
                session.add(data)

            session.commit()

            count = CountDishAndQuantityCart(id_dish=dish.id_dish,quantity=dish.quantity)
            dish_quantity_value.append(count)

        data_cart = DishCartShoping(id_user=req.id_user,item=dish_quantity_value)
        return ResponceAddCart(success=True, error= None, items=data_cart)


@app.post("/update_cart")
def update_cart_dish(req:RequestAddCart,id: int):
     dish_quantity_value = []
     with Session() as session:
        for dish in req.item:
            if not req.item and not req.id_user:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    content={"error": "ОДНО ИЗ ПОЛЕЙ ДОЛЖНО БЫТЬ ЗАПОЛЕННО item, id_user"})
            cart_update = session.query(ShoppingCartInDB).filter(ShoppingCartInDB.id == id).first()
            if not cart_update:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    content={"error": "блюдо не найдено"})
            if req.id_user:
                cart_update.id_user = req.id_user
            if req.item:
                cart_update.id_dish = dish.id_dish 
                cart_update.quantity = dish.quantity
                count = CountDishAndQuantityCart(id_dish=dish.id_dish,quantity=dish.quantity)
                dish_quantity_value.append(count)
        data_cart = DishCartShoping(id_user=req.id_user,item=dish_quantity_value)
        session.commit()
        return ResponceAddCart(success=True, error= None, items=data_cart)

@app.post("/search_order_user")
def search_order_user(id_user: int):
     with Session() as session:
        search_id_user = session.query(ShoppingCartInDB).filter(ShoppingCartInDB.id_user == id_user).all()
        if not search_id_user:
            return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content={"message": "Клиент не найден"})
        info_cart = []
        for i in search_id_user:
            info_cart.append(cart_info_in_db(i))
        return ResponceInfoCartShoping(success=True, error= None, items=info_cart)

@app.post("/delete_cart")
def delete_cart_dish_id(id: int):
    with Session() as session:
            delete_dish_from_cart = session.query(ShoppingCartInDB).filter(ShoppingCartInDB.id == id).delete()
            session.commit()
    if not delete_dish_from_cart:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content={"message": "Блюдо не найдено"})   
    else:
        return JSONResponse(
                status_code=status.HTTP_201_CREATED, 
                content={"message": "Блюдо успешно удалено"})
    
@app.post("/delete_cart_user")
def delete_cart_dish_id(id_user: int):
    with Session() as session:
            delete_dish_from_cart = session.query(ShoppingCartInDB).filter(ShoppingCartInDB.id_user == id_user).delete()
            session.commit()
    if not delete_dish_from_cart:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content={"message": "Клиент не найден"})   
    else:
        return JSONResponse(
                status_code=status.HTTP_201_CREATED, 
                content={"message": "Блюдо успешно удалено"})
    
@app.post("/add_order")
def add_order(req:RequestAddInfo):
    with Session() as session:
        cart_table_results = session.query(ShoppingCartInDB).filter(ShoppingCartInDB.id_user == req.info.id_user).all()
        if len(cart_table_results)<=0:
             return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST, 
                content={"message": "Корзина пуста"})

        req.info.number_phone = extract_phone(req.info.number_phone)
        if len(req.info.number_phone) < 10:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST, 
                content={"message": "Номер телефона не может быть меньше 10 цифр"})
        
        method_payment = session.query(PaymentMethodInDB).filter(PaymentMethodInDB.id == req.info.payment_id).first()
        if not method_payment:
            return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content={"message": "Нет такого способа оплаты"})
        
        new_order = info_model_to_model_db(req.info)

        session.add(new_order)
        session.commit()
        
        sorted_status = session.query(StatusOrderInDB).order_by(StatusOrderInDB.order_status.asc()).first()
        print(type(sorted_status))
        
        data_history = HistoryStatusInDB()
        data_history.id_order = new_order.id
        data_history.id_status = sorted_status.id
        data_history.date = datetime.now()

        session.add(data_history)
        session.commit()

        new_status = Status(id = sorted_status.id,status_name = sorted_status.status_name)
        
        session.commit()

        new_data = []
        for position in cart_table_results:
            new = OrderPositionInDB()
            new.id_order = new_order.id
            new.id_dish = position.id_dish
            new.quantity = position.quantity
            new_data.append(new)
        session.add_all(new_data)
        session.commit()

        session.query(ShoppingCartInDB).filter(ShoppingCartInDB.id_user == req.info.id_user).delete()
        session.commit()
        add_order = []
        for i in new_data:
            order_position = AddOrderPosition(id_order=i.id_order, id_dish=i.id_dish, quantity=i.quantity)
            add_order.append(order_position)
        
        return ResponseAddInfoOrder(success = True, error="", order = req.info ,positions=add_order,status=new_status)
        
@app.get("/list_order")
def list_order(limit: int, offset: int, token: str):
    
    with Session() as session:
        #проверка токена
        token = session.query(TokenInDB).filter(TokenInDB.token == token).first()
        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                content={"error": "Пользователь не авторизован"})

        total_order = session.query(InfoOrderInDB).filter(InfoOrderInDB.id).count()

        list_order_in_db = session.query(InfoOrderInDB).order_by(InfoOrderInDB.id.desc()).limit(limit).offset(offset)
        list_order = []
        for i in list_order_in_db:
            list_order.append(info_fullorder_model(i))
        return ResponceFullInfoOrder(success=True, error= "", order_list=list_order,total=total_order,limit=limit,offset=offset)
    
@app.post("/search_status")
def search_status(id:int):
    with Session() as session:
        search_status_id = session.query(StatusOrderInDB).filter(StatusOrderInDB.id == id).all()
        if not search_status_id:
            return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content={"message": "Нет такого статуса"})
        info_status = []
        for i in search_status_id:
            info_status.append(status_order_in_db(i))
        return ResponceStatusOrder(success=True, error= "", items=info_status)
    

@app.post("/search_status_upon_order")
def search_status_upon_order(order_status:int):
    with Session() as session:
        search_status = session.query(StatusOrderInDB).filter(StatusOrderInDB.order_status == order_status).all()
        if not search_status:
            return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content={"message": "Нет такого статуса"})
        info_status = []
        for i in search_status:
            info_status.append(search_status_upon_order_in_db(i))
        return ResponceSearchStatus(success=True, error= "", items=info_status) 
    
@app.post("/replacement_status")
def list_order(req:RequestReplacementStatus,id_order:int, token:str):
    with Session() as session:
        list_history = session.query(HistoryStatusInDB).filter(HistoryStatusInDB.id_order == id_order).first()
        if not list_history:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, 
                content={"error": "Такого заказа не существует"})
        current_status = (session.query(HistoryStatusInDB).filter(HistoryStatusInDB.id_order == id_order).
                          order_by(HistoryStatusInDB.date.desc()).first())
        next_status = session.query(StatusOrderInDB).filter(StatusOrderInDB.id == req.id_status).first()
        if not next_status:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, 
                content={"error": "Такого статуса не существует"})
        
        search_token = session.query(TokenInDB).filter(TokenInDB.token == token).first() 
        if search_token.user.is_admin == False:
            if next_status.order_status > current_status.status.order_status:
                data_history = HistoryStatusInDB()
                data_history.id_order = current_status.id_order
                data_history.id_status = next_status.id
                data_history.date = datetime.now()

                session.add(data_history)
                session.commit()
            else:
                return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST, 
                content={"error": "Не администратор может устанавливать статус только выше текущего"})
        if search_token.user.is_admin == True:
            data_history = HistoryStatusInDB()
            data_history.id_order = current_status.id_order
            data_history.id_status = next_status.id
            data_history.date = datetime.now()

            session.add(data_history)
            session.commit()

        new_status = ReplacementStatus(id_status=req.id_status, name_status=next_status.status_name)
        session.commit()

        return ResponceReplacementStatus(success=True,error="", status=new_status)

@app.get("/list_status")
def list_status():
    with Session() as session:
        list_status_in_db = session.query(StatusOrderInDB).all()
        list_status_order = []
        for i in list_status_in_db:
                list_status_order.append(create_status_list_in_db_order_status(i))
        return ResponceStatusList(success=True, error= None, items=list_status_order)
  

@app.get("/search_next_order_status")
def search_next_order_status(id:int):
    with Session() as session:
        search_id_status = session.query(StatusOrderInDB).filter(StatusOrderInDB.id == id).first()
        if not search_id_status:
            return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content={"message": "Нет такого статуса"})
        next_status = search_id_status.order_status + 1
        new_status = session.query(StatusOrderInDB).filter(StatusOrderInDB.order_status == next_status).all()
        if not new_status:
            return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content={"message": "Нет такого статуса"})
        info_status = []
        for i in new_status:
            info_status.append(search_status_upon_order_in_db(i))
        return ResponceSearchStatus(success=True, error= "", items=info_status)
 
@app.get("/filling_history_status")
def filling_history_status(req:RequestHistoryStatus): 
    with Session() as session:
        table_order = session.query(OrderPositionInDB).filter(OrderPositionInDB.id_order == req.item.id_order).first() 
        if not table_order:
            return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content={"message": "Нет такого заказа"})
        
        table_status = session.query(StatusOrderInDB).filter(StatusOrderInDB.id== req.item.id_status).first() 
        if not table_status:
            return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content={"message": "Нет такого статуса"})
        
        history_order = history_order_model_to_model_db(req.item)

        session.add(history_order)
        session.commit()
        
        return ResponceHistoryStatus(success = True, error="", history=req.item)
    

@app.post("/register")
async def create_user(req:RequestCreateUsers,token:str):
    with Session() as session:
        token = session.query(TokenInDB).filter(TokenInDB.token == token).first()
        if token:
            if token.user.is_admin == False:
                return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN, 
                content={"error": "Пользователь не является администратором"})
            else:
                user = session.query(UsersInDB).filter(UsersInDB.login == req.user.login).first()
                if user:
                    return JSONResponse(
                    status_code=status.HTTP_205_RESET_CONTENT, 
                    content={"error": "Пользователь с таким логином уже есть, придумайте другой логин для регистрации"})
                if req.user.password != req.user.password_check:
                    return JSONResponse(
                    status_code=status.HTTP_205_RESET_CONTENT, 
                    content={"error": "Пароли не совпадают, попробуйте еще раз"})
        
        hasher = hashlib.sha512(req.user.password.encode())
        hash_password = hasher.hexdigest()
        
    register = UsersInDB()
    register.login = req.user.login
    register.password = hash_password
    register.is_admin = req.user.is_admin

    session.add(register)
    session.commit()

    return ResponceCreateUsers(success = True,error="", user = user_in_db_to_user(register))


@app.get("/list_user")
async def list_user(token: str):
    with Session() as session:
        token = session.query(TokenInDB).filter(TokenInDB.token == token).first()
        if not token:
            return ResponceSearchToken(success=False, error= "Пользователь не авторизирован")
        result = session.query(UsersInDB).all()
        list_user = []
        for i in result:
                list_user.append(user_in_db_to_user(i))
        return ResponceListUsers(success=True, error= "", user=list_user)
    
@app.get("/search_user")
async def search_user(id: int,token:str):
    with Session() as session:
        token = session.query(TokenInDB).filter(TokenInDB.token == token).first()
        if not token:
            return ResponceSearchToken(success=False, error= "Пользователь не авторизирован")
        
        result = session.query(UsersInDB).filter(UsersInDB.id == id).all()
        if not result:
            return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content={"message": "Нет такого пользователя"})
        data_user = []
        for i in result:
                data_user.append(user_in_db_to_user(i))
        return ResponceSearchUsers(success=True, error= "", user=data_user)


@app.get("/logout")
async def search_user(token:str, all: bool):
    with Session() as session:
        if all == True:
            user = session.query(TokenInDB).filter(TokenInDB.token == token).first()
            print(user)

            delete_all_users = session.query(TokenInDB).filter(TokenInDB.id_user == user.id_user).all()

            session.query(TokenInDB).filter(TokenInDB.token == delete_all_users).delete()
            session.commit()
            return True

        if all != True:
            session.query(TokenInDB).filter(TokenInDB.token == token).delete()
            session.commit()
            return True
        else:
            return False


@app.post("/update_user")
async def search_user(req:RequestUpdateUser,id: int,token: str):
    with Session() as session:
        token = session.query(TokenInDB).filter(TokenInDB.token == token).first()
        if not token:
            return ResponceSearchToken(success=False, error= "Пользователь не авторизирован")
        
        if not req.login and not req.password and not req.password_check and not req.is_admin:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST, 
                content={"error": "ОДНО ИЗ ПОЛЕЙ ДОЛЖНО БЫТЬ ЗАПОЛЕННО login, password, password_check, is_admin"})
        user = session.query(UsersInDB).filter(UsersInDB.id == id).first()
        if not user:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, 
                content={"error": "Пользователь не найден"})
        if req.login:
            if session.query(UsersInDB).filter(UsersInDB.login == req.login).first():
                return JSONResponse(
                    status_code=status.HTTP_205_RESET_CONTENT, 
                    content={"error": "Новый логин не должен совпадать со старым"})
            user.login = req.login     
        if req.password:
            if session.query(UsersInDB).filter(UsersInDB.password == req.password).first():
                return JSONResponse(
                    status_code=status.HTTP_205_RESET_CONTENT, 
                    content={"error": "Новый пароль не должен совпадать со старым"})
            if req.password != req.password_check:
                return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, 
                content={"error": "Пароли не совпадают, попробуйте еще раз"})
            
            hasher = hashlib.sha512(req.password.encode())
            hash_password = hasher.hexdigest()
            user.password = hash_password

        if req.is_admin:
            user.is_admin = req.is_admin

        session.commit()

        new_data_user = UserOutUpdate(login=req.login,is_admin=req.is_admin)

        return ResponceUpdateUsers(success=True, error= "", user=new_data_user)
    
@app.post("/delete_user")
def delete_user(id: int,token: str):
    with Session() as session:
        search_token = session.query(TokenInDB).filter(TokenInDB.token == token).first()
        if search_token.user.is_admin == False:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN, 
                content={"error": "Пользователь не является администратором"})
        if not search_token:
            return ResponceSearchToken(success=False, error= "Пользователь не авторизирован")
        session.query(TokenInDB).filter(TokenInDB.token == token).delete()
        results = session.query(UsersInDB).filter(UsersInDB.id == id).delete()
        session.commit()    
    if not results:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content={"message": "Пользователь не найден"})   
    else:
        return JSONResponse(
                status_code=status.HTTP_201_CREATED, 
                content={"message": "Данные пользователя успешно удалены"})
    

@app.post("/checking_user")
def checking_user(req:RequestCheckingUser):
    with Session() as session:
        hasher = hashlib.sha512(req.password.encode())
        hash_password = hasher.hexdigest()
        req.password = hash_password

        
        user = session.query(UsersInDB).filter(UsersInDB.login == req.login).filter(UsersInDB.password == hash_password).first()
        if user:
            generation_token = secrets.token_hex(16)
            token = session.query(TokenInDB).filter(TokenInDB.id_user == user.id).first()
            if not token:
                token = TokenInDB()
                token.id_user = user.id
            token.token = generation_token
            session.add(token)
            session.commit()
            return ResponceCheckingUsers(success=True, error= "", user=True,token=generation_token)
        else: 
            return ResponceCheckingUsers(success=False, error= "user not found", user=False,token="")
        


        

        



from odin_doma_db_model import *

STATUS_ORDER = (
    ('В работе',0),
    ('Доставлен',1),
    ('Отменен(кухня)',2),
    ('Отменен(клиент)',3),
    ('Отменен(админ)',4),
    )

def insert_default_status():
    with Session() as session:
        status_list = session.query(StatusOrderInDB).count()
        if status_list == 0:
            for name, order in STATUS_ORDER:
               status = StatusOrderInDB()
               status.status_name = name.lower()
               status.order_status = order
               session.add(status)
            session.commit()
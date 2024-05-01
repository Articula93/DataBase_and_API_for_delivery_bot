from odin_doma_db_model import *

WEEKLY_DAY = (
    ('Понедельник','Пн',1,0),
    ('Вторник','Вт',2,1),
    ('Среда','Ср',3,2),
    ('Четверг','Чт',4,3),
    ('Пятница','Пт',5,4),
    ('Суббота','Сб',6,5),
    ('Воскресенье','Вс',7,6),
    )

def insert_default_weekly_day():
    with Session() as session:
        weekly_list = session.query(DayWeeklyInDB).count()
        if weekly_list == 0:
            for name, short_name, order, day_namber in WEEKLY_DAY:
                day_weekly = DayWeeklyInDB()
                day_weekly.name_day_weekly = name.lower()
                day_weekly.short_name = short_name.lower()
                day_weekly.order_weekly = order
                day_weekly.day_number = day_namber
                session.add(day_weekly)
            session.commit()


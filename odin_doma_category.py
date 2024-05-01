from odin_doma_db_model import *

DEFAULT_CATEGORY = (
    ('Салаты',1),
    ('Супы',2),
    ('Горячие блюда',3),
    ('Гарниры',4),
    ('Выпечка и десерты',5),
    ('Напитки',6),
    ('Добавки',7),
    )

def insert_default_category():
    with Session() as session:
        category_list = session.query(CategoryInDB).count()
        if category_list == 0:
            for name, order in DEFAULT_CATEGORY:
               category = CategoryInDB()
               category.name_category = name.lower()
               category.order_category = order
               session.add(category)
            session.commit()
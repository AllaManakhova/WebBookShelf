import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session  # модуль для соединение с бд
import sqlalchemy.ext.declarative as dec  # для объявления бд

SqlAlchemyBase = dec.declarative_base()

__factory = None  # для получения сессий подключения к бд


# Принимает на вход адрес базы данных, затем проверяет, не создали ли мы уже фабрику подключений
def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    # строка подключения (состоит из типа базы данных, адреса до базы данных и параметров подключения)
    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)

    __factory = orm.sessionmaker(bind=engine)

    # локальный всех моделей
    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


# функция для получения сессии к бд
def create_session() -> Session:
    global __factory
    return __factory()

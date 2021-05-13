from sqlalchemy import create_engine, select
from app import User, Address

engine_lite = create_engine('sqlite:///db.sqlite3')
engine_cloud = create_engine('postgresql://postgres@postgres.lan:5432/dt_test')

with engine_lite.connect() as conn_lite:
    with engine_cloud.connect() as conn_cloud:
        for table in User.metadata.sorted_tables:
            data = [dict(row) for row in conn_lite.execute(select(table.c))]
            conn_cloud.execute(table.insert().values(data))
        for table in Address.metadata.sorted_tables:
            data = [dict(row) for row in conn_lite.execute(select(table.c))]
            conn_cloud.execute(table.insert().values(data))

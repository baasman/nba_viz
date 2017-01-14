from sqlalchemy import *

engine = create_engine('sqlite:///nba_viz.db')

meta = MetaData()

averages = Table('description', meta,
                 Column('id', Integer, primary_key=True),
                 Column('statistic', String),
                 Column('gp', Float),
                 Column('mean', Float),
                 Column('std', Float),
                 Column('min', Float),
                 Column('u25th', Float),
                 Column('median', Float),
                 Column('u75th', Float),
                 Column('umax', Float),
                 Column('date_added', DateTime)
                 )

meta.create_all(engine)


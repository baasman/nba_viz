from constants import teams, var_view_map
from nba_py.team import TeamGameLogs
import numpy as np
from collections import namedtuple
from datetime import datetime
from sqlalchemy import *

desc = namedtuple('desc', ['statistic', 'gp', 'mean', 'std', 'u25th',
                           'median', 'u75th', 'umax', 'date_added'])

all_stats = list(var_view_map.values())


def _color(value):
    if value['WL'] == 'W':
        return 'orange'
    else:
        return 'grey'


def _alpha(value):
    if value['WL'] == 'W':
        return .9
    else:
        return .25


def insert_leage_average(engine, teams_dict, stat):
    meta = MetaData()
    with engine.connect() as conn:
        table = Table('description', meta, autoload=True,
                      autoload_with=conn)

        gp = np.zeros((30,))
        mean = np.zeros((30,))
        std = np.zeros((30,))
        min = np.zeros((30,))
        _25th = np.zeros((30,))
        median = np.zeros((30,))
        _75th = np.zeros((30,))
        _max = np.zeros((30,))

        for i, key in enumerate(teams):
            print(key)
            value = teams[key]
            df = TeamGameLogs(value).info()
            descr = df[stat].describe()

            gp[i] = descr[0]
            mean[i] = descr[1]
            std[i] = descr[2]
            min[i] = descr[3]
            _25th[i] = descr[4]
            median[i] = descr[5]
            _75th[i] = descr[6]
            _max[i] = descr[7]

        stat_desc = dict(statistic=stat, gp=round(np.mean(gp), 2),
                         mean=round(np.mean(mean), 2),
                         std=round(np.mean(std), 2),
                         min=round(np.mean(min), 2),
                         u25th=round(np.mean(_25th), 2),
                         median=round(np.mean(median), 2),
                         u75th=round(np.mean(_75th), 2),
                         umax=round(np.mean(_max), 2),
                         date_added=datetime.now())
        ins = table.insert()
        conn.execute(ins, stat_desc)


def get_latest(engine, stat):
    meta = MetaData()
    with engine.connect() as conn:
        table = Table('description', meta, autoload=True,
                      autoload_with=conn)
        sel = select([table.c.gp, table.c.mean, table.c.std, table.c.min,
                      table.c.u25th, table.c.median, table.c.u75th,
                      table.c.umax]).\
              where(table.c.statistic == stat).\
              order_by(table.c.date_added.desc()).\
              limit(1) # noqa
        return conn.execute(sel).fetchone()


if __name__ == '__main__':
    engine = create_engine('sqlite:///nba_viz.db')
    # for i in all_stats:
    #     tp = insert_leage_average(engine, teams, i)
    d = get_latest(engine, 'AST')
    print(d['min'])

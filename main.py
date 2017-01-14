from constants import teams, var_view_map
from nba_py.team import TeamGameLogs
from helper_funcs import _color, _alpha, get_latest
import pandas as pd

from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.widgets import Slider, Select, Button, DataTable, TableColumn
from bokeh.io import curdoc
from sqlalchemy import create_engine

engine = create_engine('sqlite:///nba_viz.db')

team_options = list(teams.keys())
begin = Slider(title="First game", start=0,
               end=82, value=0, step=1)
end = Slider(title="Last game (defaults to latest)", start=1,
             end=82, value=82, step=1)
team_selection = Select(title='Team', value='GSW', options=team_options)
y_axis = Select(title='Statistic to plot',
                options=sorted(var_view_map.keys()), value='Assists')


view_data = Button(label='View Data!', button_type='success')

source = ColumnDataSource(data=dict(x=[], y=[], yl=[], win=[],
                                    opp=[], away=[], color=[], alpha=[]))
source_average = ColumnDataSource(data=dict(team=[], games=[], mean=[], std=[],
                                            _25percentile=[], median=[],
                                            _75percentile=[], max=[]))

columns = [
    TableColumn(field='team', title='Team'),
    TableColumn(field='games', title='GP'),
    TableColumn(field="mean", title="Mean"),
    TableColumn(field="std", title="Std"),
    TableColumn(field="_25percentile", title="25th"),
    TableColumn(field="median", title="Median"),
    TableColumn(field="_75percentile", title="75th"),
    TableColumn(field="max", title="max")
]

hover = HoverTool(tooltips=[
    ('Game', '$index'),
    ('Win', '@win'),
    ('Opponent', '@opp'),
    ('Away', '@away')])

p = figure(plot_height=600, plot_width=700, title='',
           toolbar_location=None, tools=[hover])
p.circle(x='x', y='y', source=source, size=7, color='color',
         line_color=None, fill_alpha='alpha')
p.line(x='x', y='yl', source=source, line_color='red', line_width=2,
       legend='league average')
data_table = DataTable(source=source_average, columns=columns,
                       width=1000, height=300)


def select_data():
    team = team_selection.value
    data = TeamGameLogs(teams[team]).info()
    data.GAME_DATE = pd.to_datetime(data.GAME_DATE)
    data.sort_values(by='GAME_DATE', ascending=True, inplace=True)
    data.set_index(data.index[::-1] + 1, drop=True, inplace=True)

    first_game = begin.value
    last_game = min(end.value, data.shape[0])
    data = data.iloc[first_game:last_game + 1]
    data = data[data.WL.notnull()]
    data['Away'] = data.apply(lambda x: '@' in x['MATCHUP'], axis=1)
    data['Opp'] = data.apply(lambda x: x['MATCHUP'][-3:], axis=1)

    stat = var_view_map[y_axis.value]

    selection = data[['Opp', 'GAME_DATE', 'WL', 'Away', stat]]
    selection['color'] = selection.apply(_color, axis=1)
    selection['alpha'] = selection.apply(_alpha, axis=1)
    return selection


def update():
    df = select_data()
    y_lab = var_view_map[y_axis.value]

    p.title.text = 'Variable: %s' % y_axis.value
    p.xaxis.axis_label = 'Game of season'
    p.yaxis.axis_label = y_axis.value

    averages = df[y_lab].describe()
    league_average = get_latest(engine, y_lab)
    avg_for_line = league_average['mean']
    yl = [avg_for_line] * df.shape[0]
    df['yl'] = yl

    source_average.data = dict(
        team=[team_selection.value, 'league avg'],
        games=[round(averages['count'], 2), league_average['gp']],
        mean=[round(averages['mean'], 2), league_average['mean']],
        std=[round(averages['std'], 2), league_average['std']],
        min=[round(averages['min'], 2), league_average['min']],
        _25percentile=[round(averages['25%'], 2), league_average['u25th']],
        median=[round(averages['50%'], 2), league_average['median']],
        _75percentile=[round(averages['75%'], 2), league_average['u75th']],
        max=[round(averages['max'], 2), league_average['umax']],
    )

    source.data = dict(
        x=df.index.values,
        y=df[y_lab],
        yl=df['yl'],
        color=df['color'],
        alpha=df['alpha'],
        win=df['WL'],
        opp=df['Opp'],
        away=df['Away']
    )


view_data.on_click(update)

sizing_mode = 'fixed'

inputs = widgetbox(team_selection, begin, end, y_axis, view_data,
                   sizing_mode=sizing_mode)
_layout = layout([[inputs, p], [data_table]], sizing_mode=sizing_mode)
update()

curdoc().add_root(_layout)
curdoc().title = 'I luh Behball'

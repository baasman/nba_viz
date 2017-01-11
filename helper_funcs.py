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

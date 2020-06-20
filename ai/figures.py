import plotly.graph_objects as go

from model.utils import get_categories


def players_category_histogram(df):
    categories = get_categories()
    traces = []
    for cat in reversed(categories):
        trace = go.Histogram(x=df[df.category == cat].rate,
                             marker=dict(line=dict(color='rgb(0,0,0)',
                                                   width=1.5)),
                             name=cat)
        traces.append(trace)

    layout = dict(barmode='overlay',
                  title='Users ratings',
                  xaxis=dict(title='Ratings',
                             ticklen=5,
                             zeroline=False,
                             ticks="inside"),
                  yaxis=dict(title='Count',
                             ticklen=5,
                             zeroline=False,
                             ticks="outside"))

    fig = {'data': traces, 'layout': layout}

    return fig


def categories_bars(df):
    trace = go.Bar(x=df.category.unique(), y=df.category.value_counts())

    layout = dict(barmode='group',
                  title='Users ratings',
                  xaxis=dict(title='Ratings',
                             ticklen=5,
                             zeroline=False,
                             ticks="inside"),
                  yaxis=dict(title='Count',
                             ticklen=5,
                             zeroline=False,
                             ticks="outside"))
    fig = {'data': trace, 'layout': layout}

    return fig


def categories_ratio_pie(df):
    cats = df.category.unique()
    players = df.category.value_counts()
    fig = {
        "data": [
            {
                "values": players,
                "labels": cats,
                "domain": {"x": [0, .7]},
                "hoverinfo": "label",
                "hole": .3,
                "type": "pie"
            }, ],
        "layout": {
            "title": "Categories ratio",
        }
    }
    return fig


def registration_intensity_histogram(df):
    trace1 = go.Histogram(x=df.signup_date,
                          marker=dict(color='rgba(31, 119, 180, 0.8)',
                                      line=dict(color='rgb(0,0,0)',
                                                width=1.5)))
    layout = dict(barmode='group', title='Registration Intensity',
                  xaxis=dict(title='Date', ticklen=5, zeroline=False, ticks="inside"),
                  yaxis=dict(title='Users', ticklen=5, zeroline=False, ticks="outside"))
    data = [trace1]

    fig = {'data': data, 'layout': layout}

    return fig


def player_iwin_vs_rate_scatter(df):
    trace1 = go.Scatter(
        y=df.international_win,
        x=df.rate,
        mode='markers',
        marker=dict(color='rgba(31, 119, 180, 0.8)',
                    line=dict(color='rgb(0,0,0)', width=1.5))
    )

    layout = dict(title='International wins vs Rate',
                  yaxis=dict(title='International wins', ticklen=5, zeroline=False, ticks="inside"),
                  xaxis=dict(title='Ratings', ticklen=5, zeroline=False, ticks="outside"))
    data = [trace1]

    fig = {'data': data, 'layout': layout}

    return fig


def player_win_ratio_vs_rate(df):
    trace1 = go.Scatter(
        y=(df.international_win
           + df.turkish_win) / (df.international_lose
                                + df.turkish_lose
                                + df.international_draw
                                + df.turkish_draw),
        x=df.rate,
        mode='markers',
        marker=dict(color='rgba(31, 119, 180, 0.8)',
                    line=dict(color='rgb(0,0,0)', width=1.5))
    )
    layout = dict(title='Winning rate vs Rating',
                  yaxis=dict(title='Winning ratio', ticklen=5, zeroline=False, ticks="inside"),
                  xaxis=dict(title='Rating', ticklen=5, zeroline=False, ticks="outside"))
    data = [trace1]

    fig = {'data': data, 'layout': layout}

    return fig

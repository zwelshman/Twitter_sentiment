import dash
from dash.dependencies import Output, Event, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import sqlite3
import pandas as pd
import time

#import dash_auth
#USERNAME_PASSWORD_PAIRS=[['username','password'],['Jamesbond','oddjob']]

app = dash.Dash(__name__)
#aut = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)
#server = app.server

colors = {
    'background': '#303030',
    'text': '#7FDBFF'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[ 
        
        html.H2(
            children='Sentiment Analysis',
            style={
                'textAlign': 'center',
                'color': colors['text']
        }
    ),

        dcc.Input(id='sentiment_term', value='NHS', type='text',
         
         style={
                'textAlign': 'center',
                'color': colors['background']
        }
    ),
        dcc.Graph(id='live-graph', animate=False),
        dcc.Interval(
            id='graph-update',
            interval=1*10000
            
        ),

    ]
)

@app.callback(Output('live-graph', 'figure'), 
              [Input(component_id='sentiment_term', component_property='value')],
              events=[Event('graph-update', 'interval')])
def update_graph_scatter(sentiment_term):
    try:
        conn = sqlite3.connect('twitterDatabase.db')
        c = conn.cursor()
        df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 100000", conn ,params=('%' + sentiment_term + '%',))
        df.sort_values('unix', inplace=True)
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/2)).mean()

        df['date'] = pd.to_datetime(df['unix'],unit='ms')
        df.set_index('date', inplace=True)

        df = df.resample('3500s').mean()
        df.dropna(inplace=True)
        X = df.index
        Y = df.sentiment_smoothed

        data = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Scatter',
                mode= 'lines',
                line=dict(color="DarkOrange", width=4)

                )

        return {'data': [data],'layout' : go.Layout(xaxis=dict(showgrid=True, gridwidth=0, gridcolor='#4e5152', range=[min(X),max(X)]), 
                                                    yaxis=dict(showgrid=True, gridwidth=0, gridcolor='#4e5152',range=[min(Y),max(Y)]),
                                                    paper_bgcolor=colors['background'],
                                                    plot_bgcolor=colors['background'],
                                                    font = {
                                                        'color': colors['text']},
                                                    title='Term: {}'.format(sentiment_term))}

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')

if __name__ == '__main__':
    app.run_server(debug=True)
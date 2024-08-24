import os
import yaml
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

from config_reader import Config
import executor

config = Config() # reding config - yaml file
folder_data_path = config.folder_data_path # 'data'
parsed_data_filename = config.parsed_data_filename  # 'parsed_humo_messages.csv'
file_data_path = os.path.join(folder_data_path, parsed_data_filename)

# loading df with all data
def load_data_from_csv():
    try:
        df = pd.read_csv(file_data_path)
        df['tg_message_time'] = pd.to_datetime(df['tg_message_time'], format='%Y-%m-%d %H:%M:%S')
        df['transaction_time'] = pd.to_datetime(df['transaction_time'], format='%Y-%m-%d %H:%M:%S')
        return df
    except FileNotFoundError:
        df = pd.DataFrame(columns=['card', 'tg_message_time', 'transaction_time', 'location', 'amount', 'transaction_type'])
        return df

app = dash.Dash(__name__)
df = load_data_from_csv()

app.layout = html.Div([
    html.H1("Анализ трат и поступлений по картам HUMO", style={'textAlign': 'center'}),
    
    # card filter
    dcc.Dropdown(
        id='card-dropdown',
        options=[{'label': 'Все карты', 'value': 'ALL'}] + [{'label': card, 'value': card} for card in df['card'].unique()],
        value='ALL',
        clearable=False,
        style={'width': '50%', 'margin': '0 auto'}
    ),
    
    # type transaction filter
    html.Div([
        dcc.RadioItems(
            id='transaction-type-radio',
            options=[
                {'label': 'Траты', 'value': 0},
                {'label': 'Поступления', 'value': 1}
            ],
            value=0,
            labelStyle={'display': 'inline-block', 'margin-right': '10px'}
        )
    ], style={'textAlign': 'center', 'margin': '20px 0'}),
    
    # центрирование выбора дат
    html.Div(
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=df['transaction_time'].min() if not df.empty else None,
            end_date=df['transaction_time'].max() if not df.empty else None,
            display_format='YYYY-MM-DD',
        ),
        style={'textAlign': 'center', 'margin': '20px 0'}
    ),
    
    # button - loading and parsing data and refresh dashes
    html.Div([
        html.Button("Парсинг загруженных данных и обновление дашбордов", id='clear-data-button', n_clicks=0, style={'marginLeft': '20px'})
    ], style={'textAlign': 'center', 'margin': '20px 0'}),

    # сумма транзакций и число транзакций
    #html.Div(id='summary-stats', style={'textAlign': 'center', 'margin': '40px 0'}),
    html.Div(id='summary-stats', style={'textAlign': 'center', 'margin': '30px 0', 'fontSize': '18px'}),

    dcc.Graph(id='total-spending-graph'),
    dcc.Graph(id='transaction-count-graph'),
    dcc.Graph(id='daily-spending-graph'),
    dcc.Graph(id='daily-location-spending-graph'),
    dcc.Graph(id='weekly-spending-graph'),
    dcc.Graph(id='monthly-spending-graph')
])

@app.callback(
    [Output('clear-data-button', 'children'),
     Output('card-dropdown', 'options'),
     Output('date-picker-range', 'start_date'),
     Output('date-picker-range', 'end_date')],
    Input('clear-data-button', 'n_clicks')
)
def get_parse_refresh(n_clicks):
    if n_clicks > 0:
        try:
            executor.main_function(config)
            global df
            df = load_data_from_csv()  # Перезагрузка данных
            card_options = [{'label': 'Все карты', 'value': 'ALL'}] + [{'label': card, 'value': card} for card in df['card'].unique()]
            return f"Данные загружены и распаршены, дашборды обновлены ({n_clicks})", card_options, df['transaction_time'].min(), df['transaction_time'].max()
        except Exception as e:
            return f"Ошибка при очистке данных: {str(e)}", dash.no_update, dash.no_update, dash.no_update
    return "Загрузка и парсинг загруженных данных и обновление дашбордов", dash.no_update, dash.no_update, dash.no_update

# callback для обновления графиков и статистики
@app.callback(
    [Output('total-spending-graph', 'figure'),
     Output('daily-spending-graph', 'figure'),
     Output('daily-location-spending-graph', 'figure'),
     Output('transaction-count-graph', 'figure'),
     Output('summary-stats', 'children'),
     Output('weekly-spending-graph', 'figure'),
     Output('monthly-spending-graph', 'figure')],
    [Input('card-dropdown', 'value'),
     Input('transaction-type-radio', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graphs(selected_card, selected_type, start_date, end_date):
    if df.empty:
        empty_fig = px.scatter(title="Нет данных для отображения")
        return empty_fig, empty_fig, empty_fig, empty_fig, "Сумма транзакций: 0, Число транзакций: 0"
    
    # фильтрация данных на основе выбранной карты, типа транзакции и диапазона дат
    filtered_df = df[(df['transaction_time'] >= start_date) & 
                     (df['transaction_time'] <= end_date)]
    
    if selected_card != 'ALL':
        filtered_df = filtered_df[filtered_df['card'] == selected_card]
    
    filtered_df = filtered_df[filtered_df['transaction_type'] == selected_type]
    
    # суммарные - столбчатая диаграмма
    total_spending_fig = px.bar(
        filtered_df.groupby('location')['amount'].sum().reset_index(),
        x='location', y='amount',
        #title='Суммарные транзакции с разбивкой по торговым точкам',
        title=f'Суммарные транзакции по {"всем картам" if selected_card == "ALL" else f"карте {selected_card}"} с разбивкой по торговым точкам',
        labels={'amount': 'Сумма', 'location': 'Торговая точка'}
    )
    total_spending_fig.update_layout(xaxis_tickangle=-45)
    
    # ежедневные - линейная диаграмма
    daily_spending = filtered_df.groupby(filtered_df['transaction_time'].dt.date).agg({'amount': 'sum'}).reset_index()
    daily_spending_fig = px.line(daily_spending, x='transaction_time', y='amount',
                                 title=f'Ежедневные транзакции по {"всем картам" if selected_card == "ALL" else f"карте {selected_card}"}', markers=True)
                                 #title='Ежедневные транзакции', markers=True)
    daily_spending_fig.update_layout(xaxis_title='Дата', yaxis_title='Сумма')
    
    # ежедневные с разбивкой по локациям - столбчатая диаграмма
    daily_location_spending = filtered_df.groupby([filtered_df['transaction_time'].dt.date, 'location']).agg({'amount': 'sum'}).reset_index()
    daily_location_spending_fig = px.bar(daily_location_spending, x='transaction_time', y='amount', color='location',
                                         #title='Ежедневные транзакции с разбивкой по торговым точкам')
                                         title=f'Ежедневные транзакции по {"всем картам" if selected_card == "ALL" else f"карте {selected_card}"} с разбивкой по торговым точкам')
    daily_location_spending_fig.update_layout(xaxis_title='Дата', yaxis_title='Сумма')

    # новый график - количество транзакций по торговым точкам
    transaction_count = filtered_df.groupby('location').size().reset_index(name='count')
    transaction_count_fig = px.bar(transaction_count, x='location', y='count',
                                   #title='Число транзакций по торговым точкам',
                                   title=f'Число транзакций по {"всем картам" if selected_card == "ALL" else f"карте {selected_card} по торговым точкам"}',
                                   labels={'count': 'Число транзакций', 'location': 'Торговая точка'})
    transaction_count_fig.update_layout(xaxis_tickangle=-45)

    # расчет суммы транзакций и числа транзакций
    total_amount = filtered_df['amount'].sum()
    total_count = filtered_df.shape[0]
    summary_text = f"Сумма транзакций: {total_amount:.2f}, число транзакций: {total_count}"

    # недельные - столбчатая диаграмма
    weekly_spending = filtered_df.groupby(pd.Grouper(key='transaction_time', freq='W')).agg({'amount': 'sum'}).reset_index()
    weekly_spending_fig = px.bar(weekly_spending, x='transaction_time', y='amount', 
                                 title=f'Недельные транзакции по {"всем картам" if selected_card == "ALL" else f"карте {selected_card}"}',
                                 labels={'amount': 'Сумма трат', 'transaction_time': 'Неделя'})
    weekly_spending_fig.update_layout(xaxis_tickformat='%Y-%m-%d')

    # ежемесячные - столбчатая диаграмма
    monthly_spending = filtered_df.groupby(pd.Grouper(key='transaction_time', freq='ME')).agg({'amount': 'sum'}).reset_index()
    monthly_spending_fig = px.bar(monthly_spending, x='transaction_time', y='amount', 
                                  title=f'Ежемесячные транзакции по {"всем картам" if selected_card == "ALL" else f"карте {selected_card}"}',
                                  labels={'amount': 'Сумма трат', 'transaction_time': 'Месяц'})
    # looks awful !!!!
    #monthly_spending_fig.update_layout(xaxis_tickformat='%Y-%m')

    # looks very noice :)
    monthly_spending_fig.update_layout(
        xaxis_tickformat='%Y-%m',
        xaxis=dict(
            tickmode='linear',
            dtick='M1',
            tickformat='%Y-%m'
        )
    )

    return total_spending_fig, daily_spending_fig, daily_location_spending_fig, transaction_count_fig, summary_text, weekly_spending_fig, monthly_spending_fig


if __name__ == '__main__':
    #app.run_server(debug=True, host="0.0.0.0", port=8050) # app.run_server(debug=True, port=8050)
    app.run_server(debug=config.dash_debug_mode, host=config.dash_host, port=config.dash_port)

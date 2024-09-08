import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

class Candle:
    def __init__(self, time_start, time_end, body_open, body_close, shadow_max, shadow_min, 
                 buy_volume, sell_volume, buy_mean_price, sell_mean_price):
        self.time_start = time_start
        self.time_end = time_end
        self.body_open = body_open
        self.body_close = body_close
        self.shadow_max = shadow_max
        self.shadow_min = shadow_min
        self.buy_volume = buy_volume
        self.sell_volume = sell_volume
        self.buy_mean_price = buy_mean_price
        self.sell_mean_price = sell_mean_price

    def __str__(self):
        return (f"Candle({self.time_start} - {self.time_end}): "
                f"Open={self.body_open}, Close={self.body_close}, "
                f"High={self.shadow_max}, Low={self.shadow_min}, "
                f"Buy Volume={self.buy_volume}, Sell Volume={self.sell_volume}, "
                f"Avg Buy Price={self.buy_mean_price}, Avg Sell Price={self.sell_mean_price}")


def create_candles_df(trades, candle_duration_ns):
    # Создаем новый столбец для группировки сделок по временным интервалам
    trades['candle_interval'] = (trades['local_timestamp'] // candle_duration_ns) * candle_duration_ns
    
    # Группируем сделки по временным интервалам и вычисляем основные элементы свечи
    grouped = trades.groupby('candle_interval').agg(
        time_start=('local_timestamp', 'min'),  # Начало свечи
        time_end=('local_timestamp', 'max'),    # Конец свечи
        body_open=('price', 'first'),  # Цена открытия свечи
        body_close=('price', 'last'),  # Цена закрытия свечи
        shadow_max=('price', 'max'),   # Максимальная цена (верхняя тень)
        shadow_min=('price', 'min'),   # Минимальная цена (нижняя тень)
        
        # Средний объём сделок (buy и sell)
        buy_volume=('amount', lambda x: x[trades.loc[x.index, 'side'] == 'buy'].mean()),  # Средний объем покупок
        sell_volume=('amount', lambda x: x[trades.loc[x.index, 'side'] == 'sell'].mean()),  # Средний объем продаж
        
        # Средняя цена для покупок и продаж
        buy_mean_price=('price', lambda x: x[trades.loc[x.index, 'side'] == 'buy'].mean()),  # Средняя цена покупок
        sell_mean_price=('price', lambda x: x[trades.loc[x.index, 'side'] == 'sell'].mean())  # Средняя цена продаж
    ).reset_index()
    
    return grouped


def create_candles_from_df(candles_df):
    # List to store the Candle objects
    candles = []
    
    # Iterate over each row in the DataFrame to create Candle objects
    for _, row in candles_df.iterrows():
        candle = Candle(
            time_start=row['time_start'],
            time_end=row['time_end'],
            body_open=row['body_open'],
            body_close=row['body_close'],
            shadow_max=row['shadow_max'],
            shadow_min=row['shadow_min'],
            buy_volume=row['buy_volume'],
            sell_volume=row['sell_volume'],
            buy_mean_price=row['buy_mean_price'],
            sell_mean_price=row['sell_mean_price']
        )
        candles.append(candle)
    
    return candles


def make_candles(trades, candle_duration_ms=100000):
    # Преобразуем продолжительность в миллисекундах в наносекунды
    candle_duration_ns = candle_duration_ms * 1e3
    
    # Создание сводной таблицы с необходимыми полями
    candles_df = create_candles_df(trades, candle_duration_ns)
    
    # Создание объектов Candle из DataFrame
    candles = create_candles_from_df(candles_df)
    
    return candles

def plot_candles(candles):
    fig, ax = plt.subplots(figsize=(12, 6))
        
    # Определяем ширину тела свечи и ширину тени пропорционально количеству свечей
    candle_width = 3 / len(candles)  # Минимальная ширина тела свечи 0.4
    shadow_width = 1.5

    # Подготовка данных для отображения
    times = [candle.time_start for candle in candles]
    body_open_prices = [candle.body_open for candle in candles]
    body_close_prices = [candle.body_close for candle in candles]
    shadow_max_prices = [candle.shadow_max for candle in candles]
    shadow_min_prices = [candle.shadow_min for candle in candles]

    # Преобразуем времена в формат для matplotlib
    time_labels = [pd.to_datetime(ts * 1000, unit='ns') for ts in times]
    time_labels_num = mdates.date2num(time_labels)

    for i in range(len(candles)):
        candle = candles[i]
        color = 'green' if candle.body_close > candle.body_open else 'red'
        
        # Рисуем тело свечи (прямоугольник)
        ax.add_patch(plt.Rectangle(
            (time_labels_num[i] - candle_width / 2, min(candle.body_open, candle.body_close)),  # Нижняя левая точка
            candle_width,  # Ширина
            abs(candle.body_close - candle.body_open),  # Высота (разница между ценой открытия и закрытия)
            color=color
        ))
        
        # Рисуем верхнюю тень (линия от max до закрытия или открытия)
        ax.plot([time_labels_num[i], time_labels_num[i]], [candle.shadow_max, max(candle.body_open, candle.body_close)], 
                color=color, lw=shadow_width)
        
        # Рисуем нижнюю тень (линия от min до открытия или закрытия)
        ax.plot([time_labels_num[i], time_labels_num[i]], [candle.shadow_min, min(candle.body_open, candle.body_close)], 
                color=color, lw=shadow_width)
    
    # Настройка осей
    ax.set_xlim(min(time_labels_num), max(time_labels_num))
    ax.set_xlabel('Time')
    ax.set_ylabel('Price')
    ax.set_title('Candlestick Chart')
    
    # Форматирование оси x для отображения времени
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    
    plt.grid(True)
    plt.gcf().autofmt_xdate()  # Поворачиваем метки времени для лучшего отображения
    plt.show()

if __name__ == "__main__":
    path = 'md_sim/trades_dogeusdt.csv'
    trades = pd.read_csv(path)
    candles = make_candles(trades=trades, candle_duration_ms=1000*60*60) # Часовые свечки
    plot_candles(candles)

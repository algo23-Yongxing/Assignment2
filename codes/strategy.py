
import pandas as pd
import matplotlib.pyplot as plt

class DualMovingAverageBollingerStrategy:
    def __init__(self, data, initial_capital, transaction_cost_rate, slippage_rate, short_window, long_window, bollinger_window):
        self.data = data
        self.initial_capital = initial_capital
        self.transaction_cost_rate = transaction_cost_rate
        self.slippage_rate = slippage_rate
        self.short_window = short_window
        self.long_window = long_window
        self.bollinger_window = bollinger_window
        self.result = {}

    def calculate_signals(self):
        # 计算双均线策略的交易信号
        self.data['SMA_short'] = self.data['close'].rolling(window=self.short_window).mean()
        self.data['SMA_long'] = self.data['close'].rolling(window=self.long_window).mean()
        self.data['signal'] = 0
        self.data.loc[self.data['SMA_short'] > self.data['SMA_long'], 'signal'] = 1
        self.data.loc[self.data['SMA_short'] < self.data['SMA_long'], 'signal'] = -1

        # 计算布林带指标
        self.data['MA'] = self.data['close'].rolling(window=self.bollinger_window).mean()
        self.data['std'] = self.data['close'].rolling(window=self.bollinger_window).std()
        self.data['upper_band'] = self.data['MA'] + 2 * self.data['std']
        self.data['lower_band'] = self.data['MA'] - 2 * self.data['std']

        # 根据布林带指标调整交易信号
        self.data.loc[(self.data['signal'] == 1) & (self.data['close'] >= self.data['upper_band']), 'signal'] = -1
        self.data.loc[(self.data['signal'] == -1) & (self.data['close'] <= self.data['lower_band']), 'signal'] = 1

    def backtest(self):
        self.data['position'] = self.data['signal'].diff()
        self.data['position'].fillna(0, inplace=True)

        self.data['market_return'] = self.data['close'].pct_change()
        self.data['strategy_return'] = self.data['position'] * self.data['market_return']

        self.data['transaction_cost'] = self.transaction_cost_rate * self.data['close'] * abs(self.data['position'].diff())
        self.data['slippage'] = self.slippage_rate * self.data['close'] * abs(self.data['position'].diff())

        self.data['net_profit'] = self.data['strategy_return'] - self.data['transaction_cost'] - self.data['slippage']
        self.data['cumulative_profit'] = self.data['net_profit'].cumsum()

        self.data['balance'] = self.initial_capital + self.data['cumulative_profit']
        self.data['balance'] = self.data['balance'].clip(lower=0)

        self.result['Final Balance'] = self.data['balance'].iloc[-1]
        self.result['Cumulative Profit'] = self.data['cumulative_profit'].iloc[-1]
        self.result['Total Transaction Cost'] = self.data['transaction_cost'].sum()
        self.result['Annualized Return'] = (self.data['balance'].iloc[-1] / self.initial_capital) ** (252 / len(self.data)) - 1
        self.result['Sharpe Ratio'] = self.data['strategy_return'].mean() / self.data['strategy_return'].std() * (252 ** 0.5)
        self.result['Number of Long Trades'] = len(self.data[self.data['position'] == 1])
        self.result['Number of Short Trades'] = len(self.data[self.data['position'] == -1])

    def save_results_to_txt(self, filename):
        with open(filename, 'w') as f:
            for key, value in self.result.items():
                f.write(f"{key}: {value}\n")

    def plot_results(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.data.index, self.data['balance'])
        plt.title('Total Capital Curve')
        plt.xlabel('Date')
        plt.ylabel('Total Capital')
        plt.grid(True)
        plt.show()

# 加载分钟频数据
data = pd.read_csv(r'D:\CUHK\23Term2\MFE 5210\Project\marketdata\pingan.csv')

# 设定策略参数
initial_capital = 1000000
transaction_cost_rate = 0.0001
slippage_rate = 0.0001
short_window = 20
long_window = 60
bollinger_window = 40

# 创建双均线+布林带策略对象
strategy = DualMovingAverageBollingerStrategy(data, initial_capital, transaction_cost_rate, slippage_rate, short_window, long_window, bollinger_window)

# 执行策略并进行回测
strategy.calculate_signals()
strategy.backtest()

# 保存结果到txt文件
strategy.save_results_to_txt(r'D:\CUHK\23Term2\MFE 5210\Project\marketdata\backtest_results.txt')

# 绘制回测结果
strategy.plot_results()

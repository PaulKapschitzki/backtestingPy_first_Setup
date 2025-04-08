from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA
import yfinance as yf
import pandas as pd

# Performance: Wenn du viele Ticker testen möchtest, kann dies zeitaufwändig sein. Du könntest parallele Verarbeitung (z. B. mit concurrent.futures) verwenden, um die Laufzeit zu verkürzen.
# Speicherbedarf: Wenn du viele Ticker gleichzeitig verarbeitest, stelle sicher, dass genügend Speicher verfügbar ist.
# Ergebnisse speichern: Du kannst die Ergebnisse in einer Datei (z. B. CSV oder JSON) speichern, um sie später zu analysieren.

# Definiere eine Handelsstrategie
class SmaCross(Strategy):
    n1 = 10  # Periode für den kurzen gleitenden Durchschnitt
    n2 = 20  # Periode für den langen gleitenden Durchschnitt

    def init(self):
        # Berechne die gleitenden Durchschnitte
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)

    def next(self):
        # Kaufe, wenn der kurze gleitende Durchschnitt den langen kreuzt
        if crossover(self.sma1, self.sma2):
            self.buy()
        # Verkaufe, wenn der lange gleitende Durchschnitt den kurzen kreuzt
        elif crossover(self.sma2, self.sma1):
            self.sell()

# Lade historische Daten von Yahoo Finance
# def get_data(ticker, start, end):
#     data = yf.download(ticker, start=start, end=end)
#     data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
#     return data
def download_daily_data(ticker, start_date, end_date):
    """
    Download daily stock data for the given ticker and date range.
    
    Parameters:
    - ticker: Stock ticker to download data for.
    - start_date: Start date for the data download (YYYY-MM-DD).
    - end_date: End date for the data download (YYYY-MM-DD).
    
    Returns:
    - DataFrame containing the daily stock data.
    """
    # Download the data
    data = yf.download(ticker, start=start_date, end=end_date, interval='1d', auto_adjust=True)

    # Debug: Spalten ausgeben
    print(f"Spalten für {ticker}: {data.columns.tolist()}")
    
    # Check if any data was returned
    if data.empty:
        raise ValueError(f"No data returned for ticker {ticker}. Please check the ticker and date range.")
    
    # Ensure the required columns are present
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in required_columns:
        if col not in data.columns:
            raise ValueError(f"Missing required column '{col}' in data for ticker {ticker}.")
    
    # Select only the required columns
    olhcv_data = data[required_columns]
    
    # Ensure the index is a DatetimeIndex
    if not isinstance(olhcv_data.index, pd.DatetimeIndex):
        raise ValueError(f"Index is not a DatetimeIndex for ticker {ticker}.")
    
    return olhcv_data
    
    # data object mit mehreren paramtern versehen, für Splits, Dividends, etc.
    # olhcv_data['Splits'] = data['Splits']
    
    # Rename columns to match OLHCV format
    # olhcv_data.columns = ['Open', 'Low', 'High', 'Close', 'Volume']

if __name__ == "__main__":
    # Liste von Tickersymbolen, die getestet werden sollen
    tickers = ["AAPL", "MSFT", "GOOGL"]  # Beispiel: Apple, Microsoft, Google
    start_date = "2020-01-01"
    end_date = "2023-01-01"

    # Ergebnisse für jeden Ticker speichern
    results = {}

    for ticker in tickers:
        print(f"Backtesting für {ticker} läuft...")
        try:
            # Lade die Daten für den aktuellen Ticker
            data = download_daily_data(ticker, start_date, end_date)

            # Führe das Backtesting durch
            bt = Backtest(data, SmaCross, cash=10000, commission=.002)
            stats = bt.run()

            # Ergebnisse speichern
            results[ticker] = stats

            # Ergebnisse anzeigen
            print(f"Ergebnisse für {ticker}:")
            print(stats)

            # Optional: Plot für jeden Ticker anzeigen
            bt.plot()

        except Exception as e:
            print(f"Fehler beim Backtesting für {ticker}: {e}")

    # Zusammenfassung der Ergebnisse
    print("\nZusammenfassung der Backtesting-Ergebnisse:")
    for ticker, stats in results.items():
        print(f"{ticker}:")
        print(stats)
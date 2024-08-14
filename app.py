import pandas as pd
import time
import json
import ccxt

class ConfigLoader:
    """
    Kelas untuk memuat konfigurasi dari file JSON dan mengatur koneksi ke exchange.
    
    Attributes:
        filepath (str): Jalur file konfigurasi.
        api_key (str): Kunci API untuk autentikasi ke exchange.
        api_secret (str): Rahasia API untuk autentikasi ke exchange.
        enable_rate_limit (bool): Menentukan apakah pembatasan laju diaktifkan.
    """
    def __init__(self, filepath):
        """
        Inisialisasi ConfigLoader dengan jalur file konfigurasi.
        
        Args:
            filepath (str): Jalur file konfigurasi.
        """
        self.filepath = filepath
        self.api_key = ""
        self.api_secret = ""
        self.enable_rate_limit = True
        self.__load()

    def __load(self):
        """Memuat konfigurasi dari file JSON dan mengatur atribut."""
        with open(self.filepath, 'r') as f:
            config = json.load(f)
            self.api_key = config['APIKEYS']
            self.api_secret = config['SCREETS']
            self.enable_rate_limit = config['ENABLERATELIMIT']

    def get_exchange(self):
        """
        Mendapatkan instance dari ccxt.binance dengan konfigurasi yang telah ditentukan.
        
        Returns:
            ccxt.binance: Instance dari ccxt.binance yang telah dikonfigurasi.
        """
        return ccxt.binance({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': self.enable_rate_limit
        })

class DataHandler:
    """
    Kelas untuk mengambil data dari exchange dan mendeteksi anomali.
    
    Attributes:
        exchange (ccxt.binance): Instance dari ccxt.binance.
        pair (str): Pasangan mata uang yang diperdagangkan.
        timeframe (str): Kerangka waktu untuk data OHLCV.
        count (int): Jumlah data OHLCV yang diambil.
    """
    def __init__(self, exchange, pair, timeframe, count=100):
        """
        Inisialisasi DataHandler dengan konfigurasi perdagangan.
        
        Args:
            exchange (ccxt.binance): Instance dari ccxt.binance.
            pair (str): Pasangan mata uang yang diperdagangkan.
            timeframe (str): Kerangka waktu untuk data OHLCV.
            count (int): Jumlah data OHLCV yang diambil.
        """
        self.exchange = exchange
        self.pair = pair
        self.timeframe = timeframe
        self.count = count

    def fetch_data(self):
        """
        Mengambil data OHLCV dari exchange dan mengonversinya ke DataFrame.
        
        Returns:
            pd.DataFrame: DataFrame yang berisi data OHLCV dengan timestamp sebagai indeks.
        """
        data = self.exchange.fetch_ohlcv(self.pair, self.timeframe, limit=self.count)
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df

    def detect_anomalies(self, df, threshold):
        """
        Mendeteksi anomali berdasarkan selisih harga pembukaan dan penutupan.
        
        Args:
            df (pd.DataFrame): DataFrame yang berisi data OHLCV.
            threshold (float): Ambang batas persentase untuk mendeteksi anomali.
        
        Returns:
            pd.DataFrame: DataFrame yang berisi baris yang terdeteksi sebagai anomali.
        """
        df['difference'] = df['open'] - df['close'].shift(1)
        df['percentage'] = (df['difference'] / df['close'].shift(1)) * 100
        anomalies = df[df['percentage'].abs() > threshold]
        return anomalies

class TradingBot:
    """
    Kelas untuk mengelola strategi perdagangan dan menjalankan bot perdagangan.
    
    Attributes:
        exchange (ccxt.binance): Instance dari ccxt.binance.
        symbol (str): Pasangan mata uang yang diperdagangkan.
        timeframe (str): Kerangka waktu untuk data OHLCV.
        gap_threshold (float): Ambang batas persentase untuk mendeteksi anomali.
        trade_quantity (float): Jumlah yang diperdagangkan.
        data_handler (DataHandler): Instance dari DataHandler untuk mengelola data dan anomali.
    """
    def __init__(self, exchange, symbol, timeframe, gap_threshold, trade_quantity):
        """
        Inisialisasi TradingBot dengan konfigurasi perdagangan.
        
        Args:
            exchange (ccxt.binance): Instance dari ccxt.binance.
            symbol (str): Pasangan mata uang yang diperdagangkan.
            timeframe (str): Kerangka waktu untuk data OHLCV.
            gap_threshold (float): Ambang batas persentase untuk mendeteksi anomali.
            trade_quantity (float): Jumlah yang diperdagangkan.
        """
        self.exchange = exchange
        self.symbol = symbol
        self.timeframe = timeframe
        self.gap_threshold = gap_threshold
        self.trade_quantity = trade_quantity
        self.data_handler = DataHandler(exchange, symbol, timeframe)

    def place_order(self, action, quantity):
        """
        Menempatkan order beli atau jual berdasarkan aksi yang ditentukan.
        
        Args:
            action (str): Tindakan yang dilakukan ('buy' atau 'sell').
            quantity (float): Jumlah yang diperdagangkan.
        
        Returns:
            dict: Respon dari exchange setelah menempatkan order.
        
        Raises:
            ValueError: Jika aksi bukan 'buy' atau 'sell'.
        """
        if action == 'buy':
            return self.exchange.create_market_buy_order(self.symbol, quantity)
        elif action == 'sell':
            return self.exchange.create_market_sell_order(self.symbol, quantity)
        else:
            raise ValueError("Action must be 'buy' or 'sell'")

    def process_trading_strategy(self):
        """
        Memproses strategi perdagangan berdasarkan anomali yang terdeteksi.
        - Membeli jika anomali terdeteksi dan memenuhi ambang batas.
        - Menjual ketika anomali telah tertutup.
        """
        df = self.data_handler.fetch_data()
        anomalies = self.data_handler.detect_anomalies(df, self.gap_threshold)
        if not anomalies.empty:
            latest = anomalies.iloc[-1]
            current_price = self.exchange.fetch_ticker(self.symbol)['last']
            
            if latest['percentage'] > self.gap_threshold:
                print(f"Anomaly identified: {latest['percentage']:.2f}%")
                print(f"Executing buy for {self.trade_quantity} {self.symbol}")
                self.place_order('buy', self.trade_quantity)
                
                while True:
                    df = self.data_handler.fetch_data()
                    if df.iloc[-1]['close'] >= latest['close']:
                        print(f"Anomaly closed, executing sell for {self.trade_quantity} {self.symbol}")
                        self.place_order('sell', self.trade_quantity)
                        break
                    time.sleep(60)

    def trading_loop(self):
        """
        Jalankan loop tanpa batas untuk memproses strategi perdagangan setiap 1 jam.
        """
        while True:
            self.process_trading_strategy()
            time.sleep(60 * 60)

if __name__ == '__main__':
    config_loader = ConfigLoader('./config/CONFIG.json')
    exchange = config_loader.get_exchange()
    
    symbol = 'BTC/USDT'
    timeframe = '1h'
    gap_threshold = 0.01
    trade_quantity = 0.01
    
    trading_bot = TradingBot(exchange, symbol, timeframe, gap_threshold, trade_quantity)
    trading_bot.trading_loop()

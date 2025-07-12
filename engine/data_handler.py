class DataHandler:
    '''
    Provides OHLCV market data one bar at a time
    source: str
    '''
    def __init__(self, source):
        pass

    def get_next_bar(self):
        '''
        Returns a single OHLCV bar as a dictionary.
        Example: { 'timestamp': '2023-01-01', 'open': 100.0, 'high': 101.2, 'low': 99.8, 'close': 100.5, 'volume': 50000 }
        '''
        pass
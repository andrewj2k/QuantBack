from abc import ABC, abstractmethod
class BaseStrategy:
    '''
    Abstract class that generates signals from OHLCV
    '''
    def __init__(self, lookback_window = 20, entry_threshold = 1, exit_threshold = 1):
        pass
    
    @abstractmethod
    def generate_signal(self, bar):
        '''
        bar: dict with keys [timestamp, open, high, low, close, volume]
        Returns: 'BUY', 'SELL', None
        '''
        pass

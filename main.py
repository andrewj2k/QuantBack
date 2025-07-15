from engine.data_handler import DataHandler
handler = DataHandler("data/SPY.csv")
print("First 10 bars:")

for _ in range(10):
    bar = handler.get_next_bar()
    print(bar)



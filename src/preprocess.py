import pandas as pd

def process_data(file_path):
    """
    Đọc dữ liệu từ file CSV.
    """
    data = pd.read_csv(file_path)
    return data

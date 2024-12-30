import numpy as np
import pandas as pd

def generate_mock_vibration_data(num_samples=200, anomaly_rate=0.2, failure_rate=0.1):
    """
    Tạo dữ liệu giả lập từ cảm biến rung động, bao gồm cả lỗi thiết bị.
    """
    # Giá trị bình thường: 0.1 - 1.0 m/s² (dao động nhẹ)
    normal_data = np.random.uniform(0.1, 1.0, int(num_samples * (1 - anomaly_rate - failure_rate)))

    # Giá trị bất thường: > 5.0 m/s² (dao động mạnh)
    anomalies = np.random.uniform(5.0, 10.0, int(num_samples * anomaly_rate))

    # Giá trị lỗi: Tăng dần hoặc cao liên tục (lỗi thiết bị)
    failures = np.random.uniform(7.0, 10.0, int(num_samples * failure_rate))
    failures = np.repeat(failures, 3)  # Tăng chuỗi lỗi kéo dài

    # Kết hợp dữ liệu
    combined_data = np.concatenate([normal_data, anomalies, failures])
    np.random.shuffle(combined_data)

    # Chỉ lấy đúng số lượng phần tử (num_samples)
    data = combined_data[:num_samples]

    # Thêm nhiễu Gaussian
    noise = np.random.normal(0, 0.05, len(data))  # Sai số cảm biến
    data = np.clip(data + noise, 0, 10)  # Giới hạn giá trị trong khoảng hợp lý

    # Tạo timestamp ở dạng thời gian thực
    timestamps = pd.date_range(start="2024-01-01 00:00:00", periods=num_samples, freq="min")

    # Trả về DataFrame với cột timestamp đảm bảo là datetime
    df = pd.DataFrame({"timestamp": timestamps, "vibration": data})
    df['timestamp'] = pd.to_datetime(df['timestamp'])  # Đảm bảo timestamp là datetime
    return df

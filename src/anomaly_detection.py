from sklearn.ensemble import IsolationForest

def detect_anomalies_with_iforest(data, contamination=0.1):
    """
    Phát hiện bất thường trong dữ liệu rung động bằng Isolation Forest.
    :param data: DataFrame với cột 'vibration'.
    :param contamination: Tỷ lệ bất thường trong dữ liệu (float, 0-1).
    :return: DataFrame với cột 'anomaly' đánh dấu 1 (bất thường) hoặc 0 (bình thường).
    """
    if 'vibration' not in data:
        raise ValueError("Dữ liệu không chứa cột 'vibration'.")

    model = IsolationForest(contamination=contamination, random_state=42)
    model.fit(data[['vibration']])
    data['anomaly'] = model.predict(data[['vibration']])
    data['anomaly'] = data['anomaly'].apply(lambda x: 1 if x == -1 else 0)
    return data
def detect_device_failure(data, anomaly_threshold=3, rolling_window=3):
    """
    Xác định lỗi thiết bị dựa trên số lần bất thường liên tục.
    :param data: DataFrame với cột 'anomaly'.
    :param anomaly_threshold: Số lần bất thường liên tục để coi là lỗi.
    :param rolling_window: Số mẫu cần kiểm tra trong khoảng thời gian trượt.
    :return: DataFrame với cột 'failure' đánh dấu 1 (lỗi) hoặc 0 (bình thường).
    """
    if 'anomaly' not in data:
        raise ValueError("Dữ liệu không chứa cột 'anomaly'.")

    # Xác định chuỗi bất thường liên tục bằng rolling sum
    data['failure'] = (
        data['anomaly']
        .rolling(window=rolling_window, min_periods=1)
        .sum()
        .apply(lambda x: 1 if x >= anomaly_threshold else 0)
    )
    return data

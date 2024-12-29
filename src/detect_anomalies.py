from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import Dense

def detect_isolation_forest(data):
    """
    Phát hiện bất thường sử dụng Isolation Forest.
    """
    features = data.iloc[:, 2:]  # Bỏ timestamp và device_id
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(features)
    data['anomaly'] = model.predict(features)  # -1: bất thường, 1: bình thường
    return data

def detect_dbscan(data):
    """
    Phát hiện bất thường sử dụng DBSCAN.
    """
    features = data.iloc[:, 2:]  # Bỏ timestamp và device_id
    model = DBSCAN(eps=0.5, min_samples=5)
    labels = model.fit_predict(features)
    data['anomaly'] = np.where(labels == -1, 1, 0)  # -1 là bất thường
    return data

def detect_autoencoder(data):
    """
    Phát hiện bất thường sử dụng Autoencoder.
    """
    features = data.iloc[:, 2:]  # Bỏ timestamp và device_id
    
    # Xây dựng Autoencoder
    model = Sequential([
        Dense(64, activation='relu', input_dim=features.shape[1]),
        Dense(32, activation='relu'),
        Dense(64, activation='relu'),
        Dense(features.shape[1], activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='mse')
    
    # Huấn luyện Autoencoder
    model.fit(features, features, epochs=50, batch_size=32, verbose=0)
    
    # Dự đoán và tính lỗi
    reconstructed = model.predict(features)
    mse = np.mean(np.power(features - reconstructed, 2), axis=1)
    threshold = np.percentile(mse, 95)  # Ngưỡng bất thường
    data['anomaly'] = np.where(mse > threshold, 1, 0)
    return data

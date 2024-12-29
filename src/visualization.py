import plotly.express as px

def plot_anomalies_interactive(data):
    """
    Tạo biểu đồ tương tác bằng plotly để hiển thị các bất thường trong dữ liệu IoT.
    """
    anomaly_data = data[data['anomaly'] == 1]  # Lọc chỉ các điểm bất thường
    fig = px.scatter(
        anomaly_data,
        x='timestamp',
        y='temperature',
        color='anomaly',
        title="Bất thường trong dữ liệu IoT",
        labels={'timestamp': 'Thời gian', 'temperature': 'Nhiệt độ'}
    )
    fig.update_layout(template="plotly_dark")
    return fig.to_html(full_html=False)

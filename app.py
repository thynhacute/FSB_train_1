from flask import Flask, render_template, request, send_file, session, redirect, url_for, flash
import os
import pandas as pd
from werkzeug.utils import secure_filename
from src.preprocess import process_data
from src.detect_anomalies import detect_isolation_forest, detect_dbscan, detect_autoencoder
from src.fetch_web_data import fetch_weather_data
from src.visualization import plot_anomalies_interactive
from src.mock_vibration_data import generate_mock_vibration_data
from src.anomaly_detection import detect_anomalies_with_iforest, detect_device_failure
from src.auth import auth
from src.auth import login_required
app = Flask(__name__)
app.register_blueprint(auth)
app.secret_key = 'your_secret_key_here'
UPLOAD_FOLDER = 'data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

UPLOAD_FOLDERs = 'uploads'
os.makedirs(UPLOAD_FOLDERs, exist_ok=True)
app.config['UPLOAD_FOLDERs'] = UPLOAD_FOLDERs

data = generate_mock_vibration_data(num_samples=20)
 
METHOD_DESCRIPTIONS = {
    'isolation_forest': "Isolation Forest sử dụng cây quyết định để xác định các điểm bất thường dựa trên độ xa lạ.",
    'dbscan': "DBSCAN nhóm dữ liệu theo mật độ. Các điểm dữ liệu không thuộc nhóm nào được đánh dấu là bất thường.",
    'autoencoder': "Autoencoder là mạng nơ-ron tái tạo dữ liệu. Các điểm dữ liệu có lỗi tái tạo cao được xem là bất thường."
}

def process_anomalies(data):
    """
    Định dạng lại timestamp để chỉ hiển thị ngày, giờ, phút, giây.
    """
    data['timestamp'] = pd.to_datetime(data['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    return data
from functools import wraps


@app.route('/')
@login_required
def index():
    """
    Trang chính, hiển thị các lựa chọn nhập dữ liệu IoT.
    """
    return render_template('index_sensors.html')


@app.route('/analyze_temperature', methods=['POST'])
@login_required
def analyze_temperature():
    city = request.form['city']
    method = request.form['method']
    api_key = "f885edaacd5556b3852a31de35342c0d"

    try:
        # Lấy dữ liệu thời tiết từ API
        data = fetch_weather_data(city, api_key)
        data_rows, data_columns = data.shape
        min_temperature = data["temperature_min"].min()
        max_temperature = data["temperature_max"].max()
        min_humidity = data["humidity"].min()
        max_humidity = data["humidity"].max()

        # Lưu dữ liệu vào file CSV
        file_path = os.path.join(UPLOAD_FOLDER, f"{city}_temperature.csv")
        data.to_csv(file_path, index=False)

        # Phân tích dữ liệu với phương pháp đã chọn
        if method == 'isolation_forest':
            results = detect_isolation_forest(data)
            explanation = (
                "Isolation Forest sử dụng cây quyết định để xác định các điểm cách biệt dựa trên độ xa lạ "
                "so với phần còn lại của tập dữ liệu."
            )
        elif method == 'dbscan':
            results = detect_dbscan(data)
            explanation = (
                "DBSCAN nhóm dữ liệu theo mật độ. Các điểm dữ liệu không thuộc bất kỳ cụm nào được đánh dấu "
                "là bất thường."
            )
        elif method == 'autoencoder':
            results = detect_autoencoder(data)
            explanation = (
                "Autoencoder là một mạng nơ-ron huấn luyện để tái tạo dữ liệu. Điểm nào có lỗi tái tạo cao "
                "được đánh dấu là bất thường."
            )
        else:
            explanation = "Phương pháp không xác định."

        # Xử lý dữ liệu bất thường
        results = add_status_column(results)
        results = process_anomalies(results)

        # Lưu kết quả vào CSV
        output_path = os.path.join(UPLOAD_FOLDER, f"{city}_temperature_results.csv")
        results.to_csv(output_path, index=False)

        anomalies = results[results['anomaly'] == 1]
        anomaly_count = len(anomalies)
        value_unNormal = len(results[results['status'].str.contains("Bất thường")])
        value_normal = len(results) - value_unNormal
        return render_template(
            'result_temperature.html',
            city=city,
            method=method,
            anomalies=anomalies.to_dict(orient='records'),
            anomaly_count=anomaly_count,
            explanation=explanation,
            value_normal=value_normal,
            value_unNormal=value_unNormal,
            data_type="Dự báo thời tiết",
            data_columns=data_columns,
            data_rows=data_rows,
            min_temperature=min_temperature,
            max_temperature=max_temperature,
            min_humidity=min_humidity,
            max_humidity=max_humidity
            
        )
    except Exception as e:
        return f"Lỗi: Không thể lấy dữ liệu cảm biến nhiệt độ cho '{city}'. Chi tiết lỗi: {e}"
def add_status_column(results):
    def determine_status(row):
        if row['temperature'] < 20:
            return f"Nhiệt độ {row['temperature']}°C < 20°C (quá thấp)"
        elif row['temperature'] > 40:
            return f"Nhiệt độ {row['temperature']}°C > 40°C (quá cao)"
        elif row['humidity'] < 20:
            return f"Độ ẩm {row['humidity']}% < 20% (quá khô)"
        elif row['humidity'] > 80:
            return f"Độ ẩm {row['humidity']}% > 80% (quá ẩm)"
        return "Bình thường"

    results['status'] = results.apply(determine_status, axis=1)
    return results

@app.route('/analyze_light', methods=['POST'])
@login_required
def analyze_light():
    """
    Phân tích dữ liệu cảm biến ánh sáng (từ file CSV).
    """
    file = request.files['file']
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    method = request.form['method']

    try:
        processed_data = process_data(file_path)

        if method == 'isolation_forest':
            results = detect_isolation_forest(processed_data)
        elif method == 'dbscan':
            results = detect_dbscan(processed_data)
        elif method == 'autoencoder':
            results = detect_autoencoder(processed_data)

        results = process_anomalies(results)
        output_path = os.path.join(UPLOAD_FOLDER, f"light_results_{file.filename}")
        results.to_csv(output_path, index=False)

        anomalies = results[results['anomaly'] == 1]
        anomaly_count = len(anomalies)
        anomaly_not_count = len(results[results['status'] != "Bình thường"])
        explanation = METHOD_DESCRIPTIONS.get(method, "Phương pháp không xác định.")

        return render_template(
            'result_light.html',
            method=method,
            anomalies=anomalies.to_dict(orient='records'),
            anomaly_count=anomaly_count,
            explanation=explanation,
            anomaly_not_count = anomaly_not_count
        )
    except Exception as e:
        return f"Lỗi: Không thể phân tích dữ liệu cảm biến ánh sáng. Chi tiết lỗi: {e}"

@app.route('/analyze_temperature_form', methods=['GET'])
@login_required
def analyze_temperature_form():
    """
    Hiển thị form nhập thành phố và phương pháp phát hiện bất thường (nhiệt độ).
    """
    return render_template('analyze_temperature_form.html')

@app.route('/analyze_light_form', methods=['GET'])
@login_required
def analyze_light_form():
    """
    Hiển thị form tải lên file CSV (ánh sáng, độ ẩm, khí, v.v.).
    """
    return render_template('analyze_light_form.html')
@app.route('/download-sample', methods=['GET'])
@login_required
def download_sample():
    """
    Endpoint cho phép tải file CSV mẫu.
    """
    file_path = 'data/template_sample.csv'  # Đường dẫn tới file mẫu
    return send_file(file_path, as_attachment=True)
@app.route('/view_chart', methods=['GET'])
@login_required
def view_chart():
    """
    Hiển thị biểu đồ tương tác.
    """
    file_path = os.path.join(UPLOAD_FOLDER, "web_data_results.csv")
    if not os.path.exists(file_path):
        return "Không tìm thấy dữ liệu để hiển thị biểu đồ."

    data = pd.read_csv(file_path)
    chart_html = plot_anomalies_interactive(data)
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Biểu đồ tương tác</title>
    </head>
    <body>
        <h1>Biểu đồ Bất Thường IoT</h1>
        {chart_html}
    </body>
    </html>
    """
@app.route('/upload_light', methods=['GET', 'POST'])
@login_required
def upload_light():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "Không tìm thấy file. Vui lòng tải lên file CSV."

        file = request.files['file']
        if file.filename == '':
            return "File chưa được chọn. Vui lòng chọn file CSV."

        if file:
            # Lưu file tải lên
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDERs'], filename)
            file.save(file_path)

            # Đọc file CSV
            try:
                data = pd.read_csv(file_path)
            except Exception as e:
                return f"Lỗi khi đọc file CSV: {e}"

            # Xác định phương pháp phát hiện bất thường
            method = request.form['method']

            # Phân tích dữ liệu
            if method == 'isolation_forest':
                results = detect_isolation_forest(data)
                explanation = "Isolation Forest sử dụng cây quyết định để phát hiện các điểm bất thường."
            elif method == 'dbscan':
                results = detect_dbscan(data)
                explanation = "DBSCAN nhóm dữ liệu theo mật độ. Điểm không thuộc cụm nào được đánh dấu là bất thường."
            elif method == 'autoencoder':
                results = detect_autoencoder(data)
                explanation = "Autoencoder tái tạo dữ liệu và đánh dấu điểm có lỗi tái tạo cao là bất thường."
            else:
                return "Phương pháp không xác định. Vui lòng chọn phương pháp hợp lệ."

            # Thêm cột trạng thái (bình thường/bất thường)
            results['status'] = results['anomaly'].apply(lambda x: 'Bất thường' if x == 1 else 'Bình thường')
            anomalies = results[results['anomaly'] == 1]
            anomaly_count = len(anomalies)
            # Đếm số lượng bất thường và bình thường
            value_normal = results['status'].value_counts().get('Bình thường', 0)
            value_abnormal = results['status'].value_counts().get('Bất thường', 0)

            # Trả về kết quả
            return render_template(
                'result_light.html',
                method=method,
                anomaly_count=anomaly_count,
                explanation=explanation,
                value_normal=value_normal,
                value_abnormal=value_abnormal,
                anomalies=results[results['status'] == 'Bất thường'].to_dict(orient='records')
            )

    return render_template('upload_light.html')

@app.route('/data', methods=['GET'])
@login_required
def get_data():
    """
    API trả về dữ liệu rung động và trạng thái lỗi.
    """
    global data
    data = detect_anomalies_with_iforest(data, contamination=0.3)  
    data = detect_device_failure(data, anomaly_threshold=2, rolling_window=2)
    
    data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')
    
    # Định dạng timestamp thành chuỗi thời gian thực
    data['timestamp'] = data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Trả về dữ liệu JSON
    return data.to_json(orient='records')


@app.route('/vibration_dashboard')
@login_required
def vibration_dashboard():
    """
    Hiển thị giao diện bảng dữ liệu rung động.
    """
    return render_template('vibration_dashboard.html')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)


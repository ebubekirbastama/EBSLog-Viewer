import gzip
import re
import os
import sys
import csv
import requests  # IP bilgisi almak için
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableView, QVBoxLayout, QWidget,
    QLineEdit, QHBoxLayout, QPushButton, QFormLayout, QFileDialog, QMessageBox, QLabel
)
from PyQt6.QtCore import Qt, QSortFilterProxyModel
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor

class LogViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EBSLog Viewer")
        self.setGeometry(100, 100, 1200, 800)

        # Main widget
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        # Layouts
        self.layout = QVBoxLayout()
        self.top_layout = QHBoxLayout()
        self.search_layout = QFormLayout()

        # Buttons with emojis
        self.parse_single_button = QPushButton("📄 Tek Dosyayı Pars Et")
        self.parse_single_button.setStyleSheet("background-color: #4CAF50; color: black; font-size: 14px; padding: 10px;")
        self.parse_single_button.clicked.connect(self.parse_single_file)
        self.parse_single_button.setToolTip("Tek bir log dosyasını seçip verileri işle")

        self.parse_all_button = QPushButton("🔄 Tüm Verileri Yenile")
        self.parse_all_button.setStyleSheet("background-color: #2196F3; color: black; font-size: 14px; padding: 10px;")
        self.parse_all_button.clicked.connect(self.reset_table)
        self.parse_all_button.setToolTip("Birden fazla log dosyasını seçip tüm verileri yeniden yükle")

        self.save_filtered_button = QPushButton("💾 Filtrelenmiş Verileri Kaydet")
        self.save_filtered_button.setStyleSheet("background-color: #FF5722; color: black; font-size: 14px; padding: 10px;")
        self.save_filtered_button.clicked.connect(self.save_filtered_data)
        self.save_filtered_button.setToolTip("Filtrelenmiş verileri CSV formatında kaydet")

        # Add buttons to the top layout
        self.top_layout.addWidget(self.parse_single_button)
        self.top_layout.addWidget(self.parse_all_button)
        self.top_layout.addWidget(self.save_filtered_button)

        # Search Bar and Filters for each column
        self.column_filters = {}

        # Filter for each column
        self.column_names = [
            "IP Adresi", "Tarih", "İstek Türü", "User Agent", "İstek Yanıt Türü", "Nereye İstek", "Referer", "S-port"
        ]
        for col in self.column_names:
            filter_input = QLineEdit()
            filter_input.setPlaceholderText(f"{col} için arama...")
            self.column_filters[col] = filter_input
            self.search_layout.addRow(f"{col} Filtrele:", filter_input)

        # Table View
        self.table_view = QTableView()
        self.table_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.table_view.clicked.connect(self.on_table_click)

        # Statistics Label
        self.stats_label = QLabel("İstatistikler burada görüntülenecek.")
        self.layout.addWidget(self.stats_label)

        # Add layouts to the main layout
        self.layout.addLayout(self.top_layout)
        self.layout.addLayout(self.search_layout)
        self.layout.addWidget(self.table_view)

        # Set layout
        self.main_widget.setLayout(self.layout)

        # Initialize Model
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(self.column_names)
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.table_view.setModel(self.proxy_model)

        # Connect filter changes
        for filter_input in self.column_filters.values():
            filter_input.textChanged.connect(self.filter_logs)

        self.logs_data = []

    def load_data(self, data):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.column_names)

        # Store logs for statistics
        self.logs_data = data

        for entry in data:
            row = [
                QStandardItem(entry["ip"]),
                QStandardItem(entry["tarih"]),
                QStandardItem(entry["istek_turu"]),
                QStandardItem(entry["user_agent"]),
                QStandardItem(entry["istek_yanit_turu"]),
                QStandardItem(entry["istek_url"]),
                QStandardItem(entry.get("referer", "-")),
                QStandardItem(entry.get("s_port", "-")),
            ]
            for item in row:
                item.setBackground(QColor(240, 248, 255))  # Açık mavi
            self.model.appendRow(row)

        self.table_view.resizeColumnsToContents()
        self.update_statistics()

    def filter_logs(self):
        # Check the filters for each column and apply them
        for row in range(self.model.rowCount()):
            match = True
            for col_idx, col_name in enumerate(self.column_names):
                filter_text = self.column_filters[col_name].text().lower()
                item = self.model.item(row, col_idx)
                if filter_text and filter_text not in item.text().lower():
                    match = False
                    break
            self.table_view.setRowHidden(row, not match)

    def update_statistics(self):
        # İstatistikleri hesapla
        ip_count = len(set(entry["ip"] for entry in self.logs_data))
        url_count = {}
        user_agent_count = {}
        date_count = {}

        for entry in self.logs_data:
            url_count[entry["istek_url"]] = url_count.get(entry["istek_url"], 0) + 1
            user_agent_count[entry["user_agent"]] = user_agent_count.get(entry["user_agent"], 0) + 1
            date_count[entry["tarih"]] = date_count.get(entry["tarih"], 0) + 1

        # En sık erişilen URL, User-Agent, ve en yaygın tarihleri bul
        most_frequent_url = max(url_count, key=url_count.get, default="Veri Yok")
        most_frequent_user_agent = max(user_agent_count, key=user_agent_count.get, default="Veri Yok")
        most_frequent_date = max(date_count, key=date_count.get, default="Veri Yok")

        # İstatistikleri güncelle
        stats_text = (
            f"Toplam IP sayısı: {ip_count}\n"
            f"En sık erişilen URL: {most_frequent_url}\n"
            f"En sık kullanılan User-Agent: {most_frequent_user_agent}\n"
            f"En yaygın tarihler: {most_frequent_date}\n"
        )

        self.stats_label.setText(stats_text)

    def parse_single_file(self):
        # Dosya seçme iletişim kutusu
        log_file_path, _ = QFileDialog.getOpenFileName(
            self, "Log Dosyasını Seç", str(Path.cwd()), "Log Files (*.gz)"
        )
        if log_file_path:
            parsed_logs = parse_logs(log_file_path)
            self.load_data(parsed_logs)
        else:
            print("Hiçbir dosya seçilmedi.")

    def reset_table(self):
        # Birden fazla dosya seçme iletişim kutusu
        log_files, _ = QFileDialog.getOpenFileNames(
            self, "Birden Fazla Log Dosyası Seç", str(Path.cwd()), "Log Files (*.gz)"
        )
        if log_files:
            all_parsed_logs = []
            for file_path in log_files:
                all_parsed_logs.extend(parse_logs(file_path))
            self.load_data(all_parsed_logs)
        else:
            print("Hiçbir dosya seçilmedi.")

    def save_filtered_data(self):
        # Dosya kaydetme iletişim kutusu
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Filtrelenmiş Verileri Kaydet", str(Path.cwd()), "CSV Files (*.csv)"
        )
        if not save_path:
            return  # Kullanıcı dosya seçmediyse işlemi sonlandır

        # Filtrelenmiş verileri alın
        filtered_data = []
        for row in range(self.proxy_model.rowCount()):
            row_data = []
            for col in range(self.proxy_model.columnCount()):
                index = self.proxy_model.index(row, col)
                row_data.append(index.data())
            filtered_data.append(row_data)

        # CSV'ye yazma
        with open(save_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(self.column_names)  # Başlıklar
            writer.writerows(filtered_data)  # Filtrelenmiş veriler

        print(f"Filtrelenmiş veriler başarıyla kaydedildi: {save_path}")

    def on_table_click(self, index):
        # IP adresi kolonuna tıklanıp tıklanmadığını kontrol et
        if index.column() == 0:  # 0. kolonda IP adresi var
            ip_address = index.data()
            self.show_ip_info(ip_address)

    def show_ip_info(self, ip_address):
        try:
            response = requests.get(f"https://ipinfo.io/{ip_address}/json")
            data = response.json()
            location = data.get("loc", "Bilinmiyor")
            org = data.get("org", "Bilinmiyor")
            country = data.get("country", "Bilinmiyor")
            info_text = (
                f"IP: {ip_address}\n"
                f"Lokasyon: {location}\n"
                f"Organizasyon: {org}\n"
                f"Ülke: {country}"
            )
            QMessageBox.information(self, "IP Bilgisi", info_text)
        except requests.RequestException:
            QMessageBox.warning(self, "Hata", "IP bilgisi alınamadı.")

def parse_logs(file_path):
    logs = []
    try:
        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
            for line in f:
                match = re.match(r'(\d+\.\d+\.\d+\.\d+) - - \[(.*?)\] "(.*?)" (\d+) \d+ "(.*?)" "(.*?)"', line)
                if match:
                    ip, tarih, istek, yanit_turu, referer, user_agent = match.groups()
                    istek_turu, istek_url = istek.split(" ", 1)
                    logs.append({
                        "ip": ip,
                        "tarih": tarih,
                        "istek_turu": istek_turu,
                        "user_agent": user_agent,
                        "istek_yanit_turu": yanit_turu,
                        "istek_url": istek_url,
                        "referer": referer,
                        "s_port": "80",  # Port numarasını burada varsayılan olarak 80 kabul ediyoruz
                    })
    except Exception as e:
        print(f"Hata: {e}")
    return logs

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = LogViewer()
    viewer.show()
    sys.exit(app.exec())

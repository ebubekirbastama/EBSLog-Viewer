
# EBSLog Viewer

EBSLog Viewer is a Python application that provides a graphical interface for reading, filtering, and analyzing web server log files. The application allows you to parse log files in `.gz` format, filter log data by various criteria (such as IP, URL, and User-Agent), and view statistical information about the logs.

## Features

- **Parse Log Files**: Open and parse `.gz` compressed log files.
- **Filtering**: Filter log data by IP address, request type, User-Agent, URL, etc.
- **Statistics**: View statistics such as total unique IPs, most frequent URLs, most common User-Agents, and dates.
- **IP Information**: Click on IP addresses to view location and other details.
- **CSV Export**: Save filtered data to CSV format.
- **Cross-Platform**: Works on Windows, macOS, and Linux.

## Requirements

- Python 3.6 or higher
- PyQt6
- requests

### Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/EBSLog-Viewer.git
    ```
2. Install the required dependencies:
    ```bash
    pip install PyQt6 requests
    ```

### Usage

1. Run the application:
    ```bash
    python ebslog_viewer.py
    ```
2. Click on "📄 Tek Dosyayı Pars Et" to open a single log file.
3. Use filters to refine the displayed logs.
4. Click on "💾 Filtrelenmiş Verileri Kaydet" to save the filtered logs in CSV format.

## License

This project is licensed under the Apache-2.0 license 

## Acknowledgements

- PyQt6 for the graphical interface.
- requests for IP information retrieval.

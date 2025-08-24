import sys
import numpy as np
import sys
import time
import numpy as np
import pyqtgraph as pg
import adi
from language_manager import LanguageManager
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QGroupBox,
    QGridLayout,
    QComboBox,
    QProgressBar,
    QTextEdit,
    QSplitter,
)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont
import pyqtgraph as pg
import adi
import time


class SDRConfig:
    """Централизованная конфигурация для всех настроек SDR"""
    
    # Основные параметры SDR
    DEFAULT_FREQUENCY = 868e6      # Гц
    DEFAULT_SAMPLE_RATE = 10.0e6   # Гц  
    DEFAULT_BANDWIDTH = 5.0e6      # Гц
    DEFAULT_GAIN = 30              # дБ
    DEFAULT_BUFFER_SIZE = 2048     # отсчеты
    
    # Параметры детектора сигналов
    SIGNAL_DETECTION_THRESHOLD = 100  # дБ - порог обнаружения доминирующей частоты
    LOG_THRESHOLD = 100                # дБ - порог для записи в детальный лог
    
    # Параметры временного фильтра для логирования
    FREQUENCY_LOG_TIMEOUT = 10.0       # секунды - минимальный интервал между записями одной частоты
    FREQUENCY_TOLERANCE = 50000.0      # Гц (50 кГц) - допуск для определения "того же" канала
    
    # Параметры для GUI
    GUI_CONFIG = {
        "frequency": {
            "min": 70.0,           # МГц
            "max": 6000.0,         # МГц
            "default": 868.0,      # МГц (DEFAULT_FREQUENCY / 1e6)
            "decimals": 3
        },
        "sample_rate": {
            "min": 0.5,            # МГц
            "max": 56.0,           # МГц
            "default": 10.0,       # МГц (DEFAULT_SAMPLE_RATE / 1e6)
            "decimals": 1
        },
        "bandwidth": {
            "min": 0.2,            # МГц
            "max": 56.0,           # МГц
            "default": 5.0,        # МГц (DEFAULT_BANDWIDTH / 1e6)
            "decimals": 1
        },
        "gain": {
            "min": 0,              # дБ
            "max": 76,             # дБ
            "default": 30          # дБ (DEFAULT_GAIN)
        },
        "buffer_sizes": ["1024", "2048", "4096", "8192"],
        "default_buffer": "2048"   # str(DEFAULT_BUFFER_SIZE)
    }
    
    @classmethod
    def get_default_freq_axis(cls):
        """Получить частотную ось по умолчанию"""
        return np.linspace(-cls.DEFAULT_SAMPLE_RATE / 2, 
                          cls.DEFAULT_SAMPLE_RATE / 2, 
                          cls.DEFAULT_BUFFER_SIZE)
    
    @classmethod 
    def get_default_fft_data(cls):
        """Получить массив FFT данных по умолчанию"""
        return np.zeros(cls.DEFAULT_BUFFER_SIZE)
    
    @classmethod
    def get_presets(cls):
        """Получить предустановленные конфигурации"""
        return {
            "lora_868": {
                "frequency": {"default": 868.0},
                "sample_rate": {"default": 1.0},
                "bandwidth": {"default": 0.5},
                "gain": {"default": 40},
            },
            "wifi_2.4g": {
                "frequency": {"default": 2400.0},
                "sample_rate": {"default": 20.0},
                "bandwidth": {"default": 10.0},
                "gain": {"default": 30},
            },
            "bluetooth": {
                "frequency": {"default": 2440.0},
                "sample_rate": {"default": 10.0},
                "bandwidth": {"default": 5.0},
                "gain": {"default": 35},
            },
            "868": {
                "frequency": {"default": 868.0},
                "sample_rate": {"default": 10.0},
                "bandwidth": {"default": 5.0},
                "gain": {"default": 35},
            },
            "915": {
                "frequency": {"default": 915.0},
                "sample_rate": {"default": 10.0},
                "bandwidth": {"default": 26.0},
                "gain": {"default": 35},
            },
            "fm_radio": {
                "frequency": {"default": 100.0},
                "sample_rate": {"default": 5.0},
                "bandwidth": {"default": 2.0},
                "gain": {"default": 25},
            },
            "gps_l1": {
                "frequency": {"default": 1575.42},
                "sample_rate": {"default": 10.0},
                "bandwidth": {"default": 5.0},
                "gain": {"default": 45},
            },
            "lte_2100": {
                "frequency": {"default": 2100.0},
                "sample_rate": {"default": 30.0},
                "bandwidth": {"default": 20.0},
                "gain": {"default": 30},
            },
        }
    
    @classmethod
    def update_defaults(cls, frequency=None, sample_rate=None, bandwidth=None, gain=None, buffer_size=None):
        """Обновить значения по умолчанию и синхронизировать GUI конфигурацию"""
        if frequency is not None:
            cls.DEFAULT_FREQUENCY = frequency
            cls.GUI_CONFIG["frequency"]["default"] = frequency / 1e6
            
        if sample_rate is not None:
            cls.DEFAULT_SAMPLE_RATE = sample_rate
            cls.GUI_CONFIG["sample_rate"]["default"] = sample_rate / 1e6
            
        if bandwidth is not None:
            cls.DEFAULT_BANDWIDTH = bandwidth
            cls.GUI_CONFIG["bandwidth"]["default"] = bandwidth / 1e6
            
        if gain is not None:
            cls.DEFAULT_GAIN = gain
            cls.GUI_CONFIG["gain"]["default"] = gain
            
        if buffer_size is not None:
            cls.DEFAULT_BUFFER_SIZE = buffer_size
            cls.GUI_CONFIG["default_buffer"] = str(buffer_size)
    
    @classmethod
    def update_log_threshold(cls, threshold):
        """Обновить порог логирования"""
        cls.LOG_THRESHOLD = threshold
    
    @classmethod
    def update_detection_threshold(cls, threshold):
        """Обновить порог обнаружения"""
        cls.SIGNAL_DETECTION_THRESHOLD = threshold


class PlutoThread(QThread):
    """Поток для работы с ADALM-PLUTO"""

    data_ready = pyqtSignal(np.ndarray, float, float, dict)  # samples, rssi, peak_power, dominant_freq_info
    error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.sdr = None
        self.running = False
        self.center_freq = SDRConfig.DEFAULT_FREQUENCY
        self.sample_rate = SDRConfig.DEFAULT_SAMPLE_RATE
        self.bandwidth = SDRConfig.DEFAULT_BANDWIDTH
        self.gain = SDRConfig.DEFAULT_GAIN
        self.buffer_size = SDRConfig.DEFAULT_BUFFER_SIZE

    def connect_pluto(self):
        """Подключение к ADALM-PLUTO"""
        try:
            self.sdr = adi.Pluto()
            self.sdr.rx_rf_bandwidth = int(self.bandwidth)
            self.sdr.rx_lo = int(self.center_freq)
            self.sdr.sample_rate = int(self.sample_rate)
            self.sdr.rx_hardwaregain_chan0 = self.gain
            self.sdr.rx_buffer_size = self.buffer_size
            return True
        except Exception as e:
            self.error_signal.emit(f"Ошибка подключения к PLUTO: {str(e)}")
            return False

    def disconnect_pluto(self):
        """Отключение от ADALM-PLUTO"""
        if self.sdr:
            del self.sdr
            self.sdr = None

    def update_settings(self, freq, sr, bw, gain, buf_size):
        """Обновление настроек SDR"""
        self.center_freq = freq
        self.sample_rate = sr
        self.bandwidth = bw
        self.gain = gain
        self.buffer_size = buf_size

        if self.sdr:
            try:
                self.sdr.rx_lo = int(self.center_freq)
                self.sdr.sample_rate = int(self.sample_rate)
                self.sdr.rx_rf_bandwidth = int(self.bandwidth)
                self.sdr.rx_hardwaregain_chan0 = self.gain
                self.sdr.rx_buffer_size = self.buffer_size
            except Exception as e:
                self.error_signal.emit(f"Ошибка обновления настроек: {str(e)}")

    def calculate_rssi(self, samples):
        """Расчет RSSI"""
        power_linear = np.mean(np.abs(samples) ** 2)
        rssi_dbm = 10 * np.log10(power_linear) + 30  # Приблизительная калибровка
        return rssi_dbm

    def calculate_peak_power(self, fft_data):
        """Расчет пиковой мощности из FFT"""
        peak_power_db = np.max(fft_data)
        return peak_power_db

    def find_dominant_frequency(self, fft_data, freq_axis, threshold_db=None):
        """Найти доминирующую частоту в спектре"""
        if threshold_db is None:
            threshold_db = SDRConfig.SIGNAL_DETECTION_THRESHOLD
            
        # Находим индекс максимального пика
        peak_idx = np.argmax(fft_data)
        peak_power = fft_data[peak_idx]
        
        # Проверяем, превышает ли пик пороговое значение
        if peak_power > threshold_db:
            # Частота относительно центральной частоты
            freq_offset = freq_axis[peak_idx]
            # Абсолютная частота
            absolute_freq = self.center_freq + freq_offset
            return {
                'frequency': absolute_freq,
                'freq_offset': freq_offset,
                'power': peak_power,
                'detected': True
            }
        else:
            return {'detected': False}

    def run(self):
        """Основной цикл получения данных"""
        if not self.connect_pluto():
            return

        self.running = True

        while self.running:
            try:
                # Получение данных с PLUTO
                samples = self.sdr.rx()

                # Расчет RSSI
                rssi = self.calculate_rssi(samples)

                # Расчет FFT
                fft_data = np.fft.fftshift(np.fft.fft(samples))
                fft_magnitude = 20 * np.log10(np.abs(fft_data) + 1e-12)

                # Расчет пиковой мощности
                peak_power = self.calculate_peak_power(fft_magnitude)

                # Создание частотной оси
                freq_axis = np.linspace(-self.sample_rate / 2, self.sample_rate / 2, len(fft_data))
                
                # Поиск доминирующей частоты
                dominant_freq_info = self.find_dominant_frequency(fft_magnitude, freq_axis)

                # Отправка данных в основной поток
                self.data_ready.emit(fft_magnitude, rssi, peak_power, dominant_freq_info)

                # Небольшая пауза
                self.msleep(50)

            except Exception as e:
                self.error_signal.emit(f"Ошибка получения данных: {str(e)}")
                break

        self.disconnect_pluto()

    def stop(self):
        """Остановка потока"""
        self.running = False


class PowerAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()

        # Инициализируем менеджер языков
        self.lang = LanguageManager()

        # Используем централизованную конфигурацию
        self.config = SDRConfig.GUI_CONFIG

        self.pluto_thread = PlutoThread()
        self.init_ui()
        self.setup_connections()

        # Данные для графиков - используем методы из SDRConfig
        self.fft_data = SDRConfig.get_default_fft_data()
        self.freq_axis = SDRConfig.get_default_freq_axis()
        self.rssi_history = []
        self.peak_power_history = []
        self.time_history = []
        self.start_time = time.time()
        
        # Статистика логирования
        self.log_count = 0
        
        # Временной фильтр для частот (избежание дублирования записей)
        self.frequency_log_history = {}  # {частота: время_последней_записи}

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle(self.lang.get_text("window_title"))
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создаем главный layout для размещения splitter
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)  # убираем отступы
        
        # Создаем горизонтальный splitter для изменения пропорций
        self.main_splitter = QSplitter()
        self.main_splitter.setOrientation(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)

        # Левая панель - настройки
        self.setup_control_panel()

        # Правая панель - графики
        self.setup_plots_panel()
        
        # Устанавливаем начальные пропорции (300px для левой панели, остальное для графиков)
        self.main_splitter.setSizes([300, 900])

    def setup_control_panel(self):
        """Создание панели управления"""
        control_widget = QWidget()
        control_widget.setMinimumWidth(250)  # минимальная ширина
        control_widget.setMaximumWidth(500)  # максимальная ширина для гибкости
        control_layout = QVBoxLayout(control_widget)

        # Группа выбора языка (добавляем в самый верх)
        lang_group = QGroupBox(self.lang.get_text("language"))
        lang_layout = QHBoxLayout(lang_group)

        self.language_combo = QComboBox()
        available_langs = self.lang.get_available_languages()
        for lang_code, lang_name in available_langs.items():
            self.language_combo.addItem(lang_name, lang_code)
        
        # Устанавливаем текущий язык
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == self.lang.current_language:
                self.language_combo.setCurrentIndex(i)
                break
        
        lang_layout.addWidget(self.language_combo)

        # Группа подключения
        conn_group = QGroupBox(self.lang.get_text("connection_group"))
        conn_layout = QVBoxLayout(conn_group)

        self.connect_btn = QPushButton(self.lang.get_text("connect_pluto"))
        self.disconnect_btn = QPushButton(self.lang.get_text("disconnect"))
        self.disconnect_btn.setEnabled(False)

        conn_layout.addWidget(self.connect_btn)
        conn_layout.addWidget(self.disconnect_btn)

        # Группа настроек
        settings_group = QGroupBox(self.lang.get_text("settings_group"))
        settings_layout = QGridLayout(settings_group)

        # Центральная частота
        settings_layout.addWidget(QLabel(self.lang.get_text("frequency_mhz")), 0, 0)
        self.freq_spin = QDoubleSpinBox()
        self.freq_spin.setRange(
            self.config["frequency"]["min"], self.config["frequency"]["max"]
        )
        self.freq_spin.setValue(self.config["frequency"]["default"])
        self.freq_spin.setDecimals(self.config["frequency"]["decimals"])
        settings_layout.addWidget(self.freq_spin, 0, 1)

        # Частота дискретизации
        settings_layout.addWidget(QLabel(self.lang.get_text("sample_rate_mhz")), 1, 0)
        self.sr_spin = QDoubleSpinBox()
        self.sr_spin.setRange(
            self.config["sample_rate"]["min"], self.config["sample_rate"]["max"]
        )
        self.sr_spin.setValue(self.config["sample_rate"]["default"])
        self.sr_spin.setDecimals(self.config["sample_rate"]["decimals"])
        settings_layout.addWidget(self.sr_spin, 1, 1)

        # Полоса пропускания
        settings_layout.addWidget(QLabel(self.lang.get_text("bandwidth_mhz")), 2, 0)
        self.bw_spin = QDoubleSpinBox()
        self.bw_spin.setRange(
            self.config["bandwidth"]["min"], self.config["bandwidth"]["max"]
        )
        self.bw_spin.setValue(self.config["bandwidth"]["default"])
        self.bw_spin.setDecimals(self.config["bandwidth"]["decimals"])
        settings_layout.addWidget(self.bw_spin, 2, 1)

        # Усиление
        settings_layout.addWidget(QLabel(self.lang.get_text("gain_db")), 3, 0)
        self.gain_spin = QSpinBox()
        self.gain_spin.setRange(self.config["gain"]["min"], self.config["gain"]["max"])
        self.gain_spin.setValue(self.config["gain"]["default"])
        settings_layout.addWidget(self.gain_spin, 3, 1)

        # Размер буфера
        settings_layout.addWidget(QLabel(self.lang.get_text("buffer_size")), 4, 0)
        self.buffer_spin = QComboBox()
        self.buffer_spin.addItems(self.config["buffer_sizes"])
        # Устанавливаем значение по умолчанию
        default_index = self.buffer_spin.findText(self.config["default_buffer"])
        if default_index >= 0:
            self.buffer_spin.setCurrentIndex(default_index)
        settings_layout.addWidget(self.buffer_spin, 4, 1)

        # Порог обнаружения
        settings_layout.addWidget(QLabel(self.lang.get_text("detection_threshold")), 5, 0)
        self.detection_threshold_spin = QSpinBox()
        self.detection_threshold_spin.setRange(-100, 200)  # увеличили до 200 дБ для очень мощных сигналов
        self.detection_threshold_spin.setValue(SDRConfig.SIGNAL_DETECTION_THRESHOLD)
        self.detection_threshold_spin.setSuffix(" " + self.lang.get_text("db_unit"))
        self.detection_threshold_spin.setToolTip(self.lang.get_text("detection_tooltip"))
        settings_layout.addWidget(self.detection_threshold_spin, 5, 1)

        self.apply_btn = QPushButton(self.lang.get_text("apply_settings"))

        # Группа предустановок
        presets_group = QGroupBox(self.lang.get_text("presets_group"))
        presets_layout = QVBoxLayout(presets_group)

        # Динамически создаем кнопки на основе get_presets()
        self.preset_buttons = {}
        self.create_preset_buttons(presets_layout)

        # Группа измерений
        meas_group = QGroupBox(self.lang.get_text("measurements_group"))
        meas_layout = QGridLayout(meas_group)

        meas_layout.addWidget(QLabel(self.lang.get_text("rssi")), 0, 0)
        self.rssi_label = QLabel("-")
        self.rssi_label.setStyleSheet("QLabel { font-weight: bold; color: blue; }")
        meas_layout.addWidget(self.rssi_label, 0, 1)

        meas_layout.addWidget(QLabel(self.lang.get_text("peak_power")), 1, 0)
        self.peak_power_label = QLabel("-")
        self.peak_power_label.setStyleSheet("QLabel { font-weight: bold; color: red; }")
        meas_layout.addWidget(self.peak_power_label, 1, 1)

        meas_layout.addWidget(QLabel(self.lang.get_text("center_freq")), 2, 0)
        self.center_freq_label = QLabel(
            f"{self.config['frequency']['default']:.3f} МГц"
        )
        meas_layout.addWidget(self.center_freq_label, 2, 1)

        meas_layout.addWidget(QLabel(self.lang.get_text("dominant_freq")), 3, 0)
        self.dominant_freq_label = QLabel("-")
        self.dominant_freq_label.setStyleSheet("QLabel { font-weight: bold; color: green; }")
        meas_layout.addWidget(self.dominant_freq_label, 3, 1)

        meas_layout.addWidget(QLabel(self.lang.get_text("freq_offset")), 4, 0)
        self.freq_offset_label = QLabel("-")
        self.freq_offset_label.setStyleSheet("QLabel { font-weight: bold; color: orange; }")
        meas_layout.addWidget(self.freq_offset_label, 4, 1)

        # Статус
        status_group = QGroupBox(self.lang.get_text("status_group"))
        status_layout = QVBoxLayout(status_group)

        self.status_label = QLabel(self.lang.get_text("not_connected"))
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Бесконечный прогресс
        self.progress_bar.hide()

        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar)

        # Лог ошибок
        log_group = QGroupBox(self.lang.get_text("log_group"))
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(80)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)

        # Детальный лог измерений
        detailed_log_group = QGroupBox(self.lang.get_text("detailed_log_group"))
        detailed_log_layout = QVBoxLayout(detailed_log_group)

        self.detailed_log_text = QTextEdit()
        self.detailed_log_text.setMaximumHeight(120)
        self.detailed_log_text.setReadOnly(True)
        self.detailed_log_text.setStyleSheet("QTextEdit { font-family: 'Courier New', monospace; font-size: 9pt; }")
        detailed_log_layout.addWidget(self.detailed_log_text)

        # Кнопки управления логированием
        log_controls_layout = QHBoxLayout()
        self.auto_log_checkbox = QPushButton(self.lang.get_text("auto_log"))
        self.auto_log_checkbox.setCheckable(True)
        self.auto_log_checkbox.setChecked(True)
        self.clear_log_btn = QPushButton(self.lang.get_text("clear_log"))
        log_controls_layout.addWidget(self.auto_log_checkbox)
        log_controls_layout.addWidget(self.clear_log_btn)
        detailed_log_layout.addLayout(log_controls_layout)

        # Настройки порога логирования
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel(self.lang.get_text("log_threshold")))
        self.log_threshold_spin = QSpinBox()
        self.log_threshold_spin.setRange(-100, 200)  # увеличили до 200 дБ для очень мощных сигналов
        self.log_threshold_spin.setValue(SDRConfig.LOG_THRESHOLD)
        self.log_threshold_spin.setSuffix(" " + self.lang.get_text("db_unit"))
        self.log_threshold_spin.setToolTip(self.lang.get_text("log_tooltip"))
        threshold_layout.addWidget(self.log_threshold_spin)
        detailed_log_layout.addLayout(threshold_layout)

        # Настройки временного фильтра
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel(self.lang.get_text("log_interval")))
        self.log_timeout_spin = QSpinBox()
        self.log_timeout_spin.setRange(1, 300)  # от 1 секунды до 5 минут
        self.log_timeout_spin.setValue(int(SDRConfig.FREQUENCY_LOG_TIMEOUT))
        self.log_timeout_spin.setSuffix(" " + self.lang.get_text("sec_unit"))
        self.log_timeout_spin.setToolTip(self.lang.get_text("interval_tooltip"))
        filter_layout.addWidget(self.log_timeout_spin)
        detailed_log_layout.addLayout(filter_layout)

        # Настройки допуска частоты
        tolerance_layout = QHBoxLayout()
        tolerance_layout.addWidget(QLabel(self.lang.get_text("channel_tolerance")))
        self.frequency_tolerance_spin = QSpinBox()
        self.frequency_tolerance_spin.setRange(1, 500)  # от 1 кГц до 500 кГц
        self.frequency_tolerance_spin.setValue(int(SDRConfig.FREQUENCY_TOLERANCE / 1000))  # в кГц
        self.frequency_tolerance_spin.setSuffix(" кГц")  # оставляем как есть, так как это стандартная единица
        self.frequency_tolerance_spin.setToolTip(self.lang.get_text("tolerance_tooltip"))
        tolerance_layout.addWidget(self.frequency_tolerance_spin)
        detailed_log_layout.addLayout(tolerance_layout)

        # Статистика логирования
        stats_layout = QHBoxLayout()
        stats_layout.addWidget(QLabel(self.lang.get_text("log_count")))
        self.log_count_label = QLabel("0")
        self.log_count_label.setStyleSheet("QLabel { font-weight: bold; color: blue; }")
        stats_layout.addWidget(self.log_count_label)
        stats_layout.addStretch()
        detailed_log_layout.addLayout(stats_layout)

        # Добавление групп в layout
        control_layout.addWidget(lang_group)  # добавляем группу языка первой
        control_layout.addWidget(conn_group)
        control_layout.addWidget(settings_group)
        control_layout.addWidget(self.apply_btn)
        control_layout.addWidget(presets_group)
        control_layout.addWidget(meas_group)
        control_layout.addWidget(status_group)
        control_layout.addWidget(log_group)
        control_layout.addWidget(detailed_log_group)
        control_layout.addStretch()

        # Добавляем панель управления в splitter
        self.main_splitter.addWidget(control_widget)

    def create_preset_buttons(self, presets_layout):
        """Создание кнопок предустановок динамически на основе get_presets()"""
        presets = SDRConfig.get_presets()
        
        for preset_key in presets.keys():
            # Получаем переведенное название кнопки
            button_text = self.lang.get_text(preset_key)
            
            # Создаем кнопку
            button = QPushButton(button_text)
            button.setToolTip(self.lang.get_text("preset_tooltip", preset_key))
            
            # Сохраняем ссылку на кнопку
            self.preset_buttons[preset_key] = button
            
            # Подключаем обработчик (используем closure для сохранения preset_key)
            button.clicked.connect(lambda checked, key=preset_key: self.load_preset_config(key))
            
            # Добавляем кнопку в layout
            presets_layout.addWidget(button)

    def change_language(self, language_code):
        """Изменение языка интерфейса"""
        if self.lang.set_language(language_code):
            # Обновляем заголовок окна
            self.setWindowTitle(self.lang.get_text("window_title"))
            
            # Обновляем все элементы интерфейса
            self.update_interface_texts()
            
            # Логируем изменение языка
            lang_name = self.lang.get_available_languages()[language_code]
            self.log_message(self.lang.get_text("language_changed", lang_name))

    def update_interface_texts(self):
        """Обновление всех текстов интерфейса после смены языка"""
        # Обновляем все GroupBox заголовки - нужно получить их через findChildren
        for group_box in self.findChildren(QGroupBox):
            if hasattr(group_box, 'text_key'):
                group_box.setTitle(self.lang.get_text(group_box.text_key))
        
        # Обновляем кнопки
        self.connect_btn.setText(self.lang.get_text("connect_pluto"))
        self.disconnect_btn.setText(self.lang.get_text("disconnect"))
        self.apply_btn.setText(self.lang.get_text("apply_settings"))
        self.auto_log_checkbox.setText(self.lang.get_text("auto_log"))
        self.clear_log_btn.setText(self.lang.get_text("clear_log"))
        
        # Обновляем кнопки предустановок
        for preset_key, button in self.preset_buttons.items():
            button.setText(self.lang.get_text(preset_key))
            button.setToolTip(self.lang.get_text("preset_tooltip", preset_key))
        
        # Обновляем метки полей - нужно найти их по тексту или сохранить ссылки
        # Для простоты пересоздадим интерфейс полностью
        self.recreate_interface()

    def recreate_interface(self):
        """Пересоздание интерфейса с новыми переводами"""
        # Сохраняем текущие значения
        current_freq = self.freq_spin.value()
        current_sr = self.sr_spin.value()
        current_bw = self.bw_spin.value()
        current_gain = self.gain_spin.value()
        current_buffer = self.buffer_spin.currentText()
        current_detection_threshold = self.detection_threshold_spin.value()
        current_log_threshold = self.log_threshold_spin.value()
        current_log_timeout = self.log_timeout_spin.value()
        current_tolerance = self.frequency_tolerance_spin.value()
        current_language_index = self.language_combo.currentIndex()
        
        # Сохраняем состояние подключения
        is_connected = self.disconnect_btn.isEnabled()
        
        # Очищаем splitter
        while self.main_splitter.count() > 0:
            widget = self.main_splitter.widget(0)
            widget.setParent(None)
            widget.deleteLater()
        
        # Пересоздаем панели
        self.setup_control_panel()
        self.setup_plots_panel()
        
        # Восстанавливаем значения
        self.freq_spin.setValue(current_freq)
        self.sr_spin.setValue(current_sr)
        self.bw_spin.setValue(current_bw)
        self.gain_spin.setValue(current_gain)
        
        # Находим и устанавливаем текущий буфер
        buffer_index = self.buffer_spin.findText(current_buffer)
        if buffer_index >= 0:
            self.buffer_spin.setCurrentIndex(buffer_index)
            
        self.detection_threshold_spin.setValue(current_detection_threshold)
        self.log_threshold_spin.setValue(current_log_threshold)
        self.log_timeout_spin.setValue(current_log_timeout)
        self.frequency_tolerance_spin.setValue(current_tolerance)
        self.language_combo.setCurrentIndex(current_language_index)
        
        # Восстанавливаем состояние подключения
        if is_connected:
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.status_label.setText(self.lang.get_text("connected"))
        else:
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self.status_label.setText(self.lang.get_text("not_connected"))
        
        # Восстанавливаем размеры splitter
        self.main_splitter.setSizes([300, 900])
        
        # Переподключаем сигналы (так как элементы пересозданы)
        self.setup_connections()
        
        # Обновляем подписи линий на графике
        self.update_line_labels()

    def update_line_labels(self):
        """Обновление подписей линий на графике после смены языка"""
        if hasattr(self, 'detection_threshold_line'):
            current_value = self.detection_threshold_line.getPos()[1]
            self.detection_threshold_line.label.setFormat(
                f'{self.lang.get_text("detection_line_label")}: {{value:.0f}} {self.lang.get_text("db_unit")}'
            )
            
        if hasattr(self, 'log_threshold_line'):
            current_value = self.log_threshold_line.getPos()[1] 
            self.log_threshold_line.label.setFormat(
                f'{self.lang.get_text("log_line_label")}: {{value:.0f}} {self.lang.get_text("db_unit")}'
            )

    def on_language_changed(self):
        """Обработчик смены языка"""
        current_index = self.language_combo.currentIndex()
        if current_index >= 0:
            language_code = self.language_combo.itemData(current_index)
            if language_code and language_code != self.lang.current_language:
                self.change_language(language_code)

    def setup_plots_panel(self):
        """Создание панели с графиками"""
        plots_widget = QWidget()
        plots_layout = QVBoxLayout(plots_widget)

        # FFT график
        fft_group = QGroupBox(self.lang.get_text("fft_group"))
        fft_layout = QVBoxLayout(fft_group)

        self.fft_plot = pg.PlotWidget()
        self.fft_plot.setLabel("left", self.lang.get_text("power_axis"), self.lang.get_text("db_unit"))
        self.fft_plot.setLabel("bottom", self.lang.get_text("frequency_axis"), self.lang.get_text("hz_unit"))
        self.fft_plot.showGrid(True)
        # Устанавливаем диапазон оси Y по умолчанию для отображения сигналов до 200 дБ
        self.fft_plot.setYRange(-100, 200, padding=0)
        self.fft_curve = self.fft_plot.plot(pen="g", width=2, name=self.lang.get_text("spectrum_legend"))
        
        # Добавляем интерактивные линии порогов
        # Порог обнаружения (пунктирная красная линия)
        detection_pen = pg.mkPen(color='r', style=pg.QtCore.Qt.DashLine, width=2)
        self.detection_threshold_line = pg.InfiniteLine(
            pos=SDRConfig.SIGNAL_DETECTION_THRESHOLD,
            angle=0,  # горизонтальная линия
            pen=detection_pen,
            movable=True,  # делаем перетаскиваемой
            bounds=[-100, 200],  # максимальный диапазон: от -100 до +200 дБ для очень мощных сигналов
            label=f'{self.lang.get_text("detection_line_label")}: {{value:.0f}} {self.lang.get_text("db_unit")}',
            labelOpts={'position': 0.1, 'color': (255, 0, 0), 'fill': (255, 255, 255, 100)}
        )
        self.fft_plot.addItem(self.detection_threshold_line)
        
        # Порог логирования (пунктирная оранжевая линия)
        log_pen = pg.mkPen(color='orange', style=pg.QtCore.Qt.DashDotLine, width=2)
        self.log_threshold_line = pg.InfiniteLine(
            pos=SDRConfig.LOG_THRESHOLD,
            angle=0,  # горизонтальная линия
            pen=log_pen,
            movable=True,  # делаем перетаскиваемой
            bounds=[-100, 200],  # максимальный диапазон: от -100 до +200 дБ для очень мощных сигналов
            label=f'{self.lang.get_text("log_line_label")}: {{value:.0f}} {self.lang.get_text("db_unit")}',
            labelOpts={'position': 0.9, 'color': (255, 165, 0), 'fill': (255, 255, 255, 100)}
        )
        self.fft_plot.addItem(self.log_threshold_line)
        
        # Добавляем легенду
        self.fft_plot.addLegend()

        fft_layout.addWidget(self.fft_plot)

        # RSSI график во времени
        rssi_group = QGroupBox(self.lang.get_text("rssi_group"))
        rssi_layout = QVBoxLayout(rssi_group)

        self.rssi_plot = pg.PlotWidget()
        self.rssi_plot.setLabel("left", "RSSI", self.lang.get_text("dbm_unit"))
        self.rssi_plot.setLabel("bottom", self.lang.get_text("time_axis"), self.lang.get_text("sec_unit"))
        self.rssi_plot.showGrid(True)
        self.rssi_curve = self.rssi_plot.plot(pen="b", width=2)

        rssi_layout.addWidget(self.rssi_plot)

        # Пиковая мощность во времени
        power_group = QGroupBox(self.lang.get_text("power_group"))
        power_layout = QVBoxLayout(power_group)

        self.power_plot = pg.PlotWidget()
        self.power_plot.setLabel("left", self.lang.get_text("power_axis"), self.lang.get_text("db_unit"))
        self.power_plot.setLabel("bottom", self.lang.get_text("time_axis"), self.lang.get_text("sec_unit"))
        self.power_plot.showGrid(True)
        self.power_curve = self.power_plot.plot(pen="r", width=2)

        power_layout.addWidget(self.power_plot)

        plots_layout.addWidget(fft_group)
        plots_layout.addWidget(rssi_group)
        plots_layout.addWidget(power_group)

        # Добавляем панель графиков в splitter
        self.main_splitter.addWidget(plots_widget)

    def update_config(self, new_config):
        """Обновление конфигурационных параметров"""
        self.config.update(new_config)
        # Здесь можно добавить логику для обновления уже созданных элементов интерфейса
        # если это необходимо

    def get_config(self):
        """Получение текущей конфигурации"""
        return self.config.copy()

    def load_preset_config(self, preset_name):
        """Загрузка предустановленной конфигурации"""
        presets = SDRConfig.get_presets()

        if preset_name in presets:
            # Обновляем только значения по умолчанию, сохраняя диапазоны
            for key, values in presets[preset_name].items():
                if key in self.config:
                    self.config[key].update(values)

            # Обновляем элементы интерфейса
            self.freq_spin.setValue(self.config["frequency"]["default"])
            self.sr_spin.setValue(self.config["sample_rate"]["default"])
            self.bw_spin.setValue(self.config["bandwidth"]["default"])
            self.gain_spin.setValue(self.config["gain"]["default"])

            self.log_message(self.lang.get_text("preset_loaded", preset_name))

    def setup_connections(self):
        """Настройка соединений сигналов"""
        # Основные кнопки
        self.connect_btn.clicked.connect(self.connect_pluto)
        self.disconnect_btn.clicked.connect(self.disconnect_pluto)
        self.apply_btn.clicked.connect(self.apply_settings)

        # Смена языка
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)

        # Предустановки (кнопки уже подключены в create_preset_buttons)

        # Управление логированием
        self.clear_log_btn.clicked.connect(self.clear_detailed_log)
        self.log_threshold_spin.valueChanged.connect(self.update_log_threshold)
        self.detection_threshold_spin.valueChanged.connect(self.update_detection_threshold)
        self.log_timeout_spin.valueChanged.connect(self.update_log_timeout)
        self.frequency_tolerance_spin.valueChanged.connect(self.update_frequency_tolerance)

        # Подключаем сигналы от интерактивных линий на графике (только если они существуют)
        if hasattr(self, 'detection_threshold_line'):
            self.detection_threshold_line.sigPositionChanged.connect(self.on_detection_line_moved)
        if hasattr(self, 'log_threshold_line'):
            self.log_threshold_line.sigPositionChanged.connect(self.on_log_line_moved)

        # Сигналы от потока PLUTO (подключаем только один раз при первой инициализации)
        if not hasattr(self, '_connections_setup'):
            self.pluto_thread.data_ready.connect(self.update_data)
            self.pluto_thread.error_signal.connect(self.handle_error)
            self.pluto_thread.finished.connect(self.thread_finished)
            self._connections_setup = True

    def connect_pluto(self):
        """Подключение к PLUTO"""
        self.connect_btn.setEnabled(False)
        self.progress_bar.show()
        self.status_label.setText(self.lang.get_text("connecting"))
        self.log_message(self.lang.get_text("pluto_connect_attempt"))

        # Применяем настройки перед подключением
        self.apply_settings()

        # Запускаем поток
        self.pluto_thread.start()

    def disconnect_pluto(self):
        """Отключение от PLUTO"""
        self.pluto_thread.stop()
        self.pluto_thread.wait()

    def thread_finished(self):
        """Обработка завершения потока"""
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.progress_bar.hide()
        self.status_label.setText(self.lang.get_text("not_connected"))
        self.log_message(self.lang.get_text("pluto_disconnected"))

    def apply_settings(self):
        """Применение настроек SDR"""
        freq = self.freq_spin.value() * 1e6
        sr = self.sr_spin.value() * 1e6
        bw = self.bw_spin.value() * 1e6
        gain = self.gain_spin.value()
        buf_size = int(self.buffer_spin.currentText())

        self.pluto_thread.update_settings(freq, sr, bw, gain, buf_size)

        # Обновляем частотную ось
        self.freq_axis = np.linspace(-sr / 2, sr / 2, buf_size)

        # Обновляем отображение центральной частоты
        self.center_freq_label.setText(f"{freq/1e6:.3f} МГц")

        self.log_message(self.lang.get_text("settings_updated", freq/1e6, sr/1e6))

    def update_data(self, fft_data, rssi, peak_power, dominant_freq_info):
        """Обновление данных и графиков"""
        # Обновляем статус
        if not self.disconnect_btn.isEnabled():
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.progress_bar.hide()
            self.status_label.setText(self.lang.get_text("connected"))
            self.log_message(self.lang.get_text("pluto_connected"))

        # Обновляем метрики
        self.rssi_label.setText(f"{rssi:.1f} {self.lang.get_text('dbm_unit')}")
        self.peak_power_label.setText(f"{peak_power:.1f} {self.lang.get_text('db_unit')}")

        # Обновляем информацию о доминирующей частоте
        if dominant_freq_info['detected']:
            freq_mhz = dominant_freq_info['frequency'] / 1e6
            offset_khz = dominant_freq_info['freq_offset'] / 1e3
            power_db = dominant_freq_info['power']
            
            self.dominant_freq_label.setText(f"{freq_mhz:.3f} МГц")
            self.freq_offset_label.setText(f"{offset_khz:+.1f} кГц")
            
            # Детальное логирование с временным фильтром
            if (self.auto_log_checkbox.isChecked() and 
                power_db > self.log_threshold_spin.value() and
                self.should_log_frequency(dominant_freq_info['frequency'])):
                self.log_detailed_measurement(rssi, peak_power, freq_mhz, offset_khz, power_db)
        else:
            self.dominant_freq_label.setText(self.lang.get_text("not_detected"))
            self.freq_offset_label.setText("-")

        # Обновляем FFT график
        self.fft_curve.setData(self.freq_axis, fft_data)
        
        # Обновляем или добавляем маркер доминирующей частоты
        if hasattr(self, 'peak_marker'):
            self.fft_plot.removeItem(self.peak_marker)
        
        if dominant_freq_info['detected']:
            # Добавляем маркер на доминирующую частоту
            freq_offset = dominant_freq_info['freq_offset']
            power_db = dominant_freq_info['power']
            
            # Создаем маркер в виде круга
            self.peak_marker = pg.ScatterPlotItem(
                x=[freq_offset], 
                y=[power_db], 
                symbol='o', 
                size=15, 
                brush='red', 
                pen=pg.mkPen('darkred', width=2)
            )
            self.fft_plot.addItem(self.peak_marker)

        # Обновляем исторические данные
        current_time = time.time() - self.start_time
        self.time_history.append(current_time)
        self.rssi_history.append(rssi)
        self.peak_power_history.append(peak_power)

        # Ограничиваем историю (последние 1000 точек)
        if len(self.time_history) > 1000:
            self.time_history.pop(0)
            self.rssi_history.pop(0)
            self.peak_power_history.pop(0)

        # Обновляем временные графики
        self.rssi_curve.setData(self.time_history, self.rssi_history)
        self.power_curve.setData(self.time_history, self.peak_power_history)

    def handle_error(self, error_msg):
        """Обработка ошибок"""
        self.log_message(self.lang.get_text("error_prefix", error_msg))
        self.status_label.setText(self.lang.get_text("error"))
        self.progress_bar.hide()
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)

    def log_message(self, message):
        """Добавление сообщения в лог"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def log_detailed_measurement(self, rssi, peak_power, freq_mhz, offset_khz, signal_power):
        """Детальное логирование измерений"""
        timestamp = time.strftime("%H:%M:%S.%f")[:-3]  # С миллисекундами
        threshold = self.log_threshold_spin.value()
        log_entry = (
            f"[{timestamp}] "
            f"Freq: {freq_mhz:8.3f} MHz | "
            f"Offset: {offset_khz:+7.1f} kHz | "
            f"RSSI: {rssi:6.1f} dBm | "
            f"Peak: {peak_power:6.1f} dB | "
            f"Signal: {signal_power:6.1f} dB | "
            f"(T:{threshold:+3d}dB)"
        )
        self.detailed_log_text.append(log_entry)
        
        # Обновляем счетчик
        self.log_count += 1
        self.log_count_label.setText(str(self.log_count))
        
        # Автопрокрутка к последней записи
        scrollbar = self.detailed_log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_detailed_log(self):
        """Очистка детального лога"""
        self.detailed_log_text.clear()
        self.log_count = 0
        self.log_count_label.setText("0")
        # Очищаем также историю частот
        self.frequency_log_history.clear()
        self.log_message(self.lang.get_text("log_cleared"))

    def update_log_threshold(self, value):
        """Обновление порога логирования из ползунка"""
        SDRConfig.LOG_THRESHOLD = value
        # Обновляем позицию линии на графике (без вызова сигнала)
        self.log_threshold_line.blockSignals(True)
        self.log_threshold_line.setPos(value)
        self.log_threshold_line.blockSignals(False)
        self.log_message(self.lang.get_text("log_threshold_changed", value))

    def update_log_timeout(self, value):
        """Обновление интервала временного фильтра"""
        SDRConfig.FREQUENCY_LOG_TIMEOUT = float(value)
        self.log_message(self.lang.get_text("log_interval_changed", value))

    def update_frequency_tolerance(self, value):
        """Обновление допуска частоты для определения того же канала"""
        SDRConfig.FREQUENCY_TOLERANCE = float(value * 1000)  # переводим кГц в Гц
        self.log_message(self.lang.get_text("tolerance_changed", value))

    def update_detection_threshold(self, value):
        """Обновление порога обнаружения из ползунка"""
        SDRConfig.SIGNAL_DETECTION_THRESHOLD = value
        # Обновляем позицию линии на графике (без вызова сигнала)
        self.detection_threshold_line.blockSignals(True)
        self.detection_threshold_line.setPos(value)
        self.detection_threshold_line.blockSignals(False)
        self.log_message(self.lang.get_text("detection_threshold_changed", value))

    def on_detection_line_moved(self, line):
        """Обработка перемещения линии порога обнаружения на графике"""
        new_value = int(round(line.getPos()[1]))  # Y-координата линии
        # Обновляем ползунок (без вызова сигнала)
        self.detection_threshold_spin.blockSignals(True)
        self.detection_threshold_spin.setValue(new_value)
        self.detection_threshold_spin.blockSignals(False)
        # Обновляем конфигурацию
        SDRConfig.SIGNAL_DETECTION_THRESHOLD = new_value
        self.log_message(self.lang.get_text("detection_threshold_moved", new_value))

    def on_log_line_moved(self, line):
        """Обработка перемещения линии порога логирования на графике"""
        new_value = int(round(line.getPos()[1]))  # Y-координата линии
        # Обновляем ползунок (без вызова сигнала)
        self.log_threshold_spin.blockSignals(True)
        self.log_threshold_spin.setValue(new_value)
        self.log_threshold_spin.blockSignals(False)
        # Обновляем конфигурацию
        SDRConfig.LOG_THRESHOLD = new_value
        self.log_message(self.lang.get_text("log_threshold_moved", new_value))

    def should_log_frequency(self, frequency):
        """Проверить, нужно ли логировать данную частоту (временной фильтр)"""
        current_time = time.time()
        
        # Ищем близкую частоту в истории
        for logged_freq, last_time in list(self.frequency_log_history.items()):
            # Проверяем, находится ли частота в пределах допуска
            if abs(frequency - logged_freq) <= SDRConfig.FREQUENCY_TOLERANCE:
                # Проверяем, прошло ли достаточно времени
                if current_time - last_time < SDRConfig.FREQUENCY_LOG_TIMEOUT:
                    return False  # Слишком рано для повторной записи
                else:
                    # Обновляем время для этой частоты
                    del self.frequency_log_history[logged_freq]
                    self.frequency_log_history[frequency] = current_time
                    return True
        
        # Новая частота - добавляем в историю и разрешаем логирование
        self.frequency_log_history[frequency] = current_time
        
        # Очищаем старые записи (старше 1 часа)
        cutoff_time = current_time - 3600  # 1 час
        self.frequency_log_history = {
            freq: log_time for freq, log_time in self.frequency_log_history.items()
            if log_time > cutoff_time
        }
        
        return True

    def save_splitter_state(self):
        """Сохранение состояния splitter"""
        sizes = self.main_splitter.sizes()
        # Можно сохранить в настройки приложения или файл
        # Для простоты пока просто выводим в лог
        total_width = sum(sizes)
        if total_width > 0:
            left_percent = (sizes[0] / total_width) * 100
            self.log_message(self.lang.get_text("proportions_saved", left_percent, 100-left_percent))

    def restore_splitter_state(self):
        """Восстановление состояния splitter"""
        # Устанавливаем разумные пропорции по умолчанию
        self.main_splitter.setSizes([300, 900])

    def closeEvent(self, event):
        """Обработка закрытия приложения"""
        # Сохраняем состояние splitter
        self.save_splitter_state()
        
        if self.pluto_thread.isRunning():
            self.pluto_thread.stop()
            self.pluto_thread.wait()
        event.accept()


def main():
    app = QApplication(sys.argv)

    # Настройка стиля PyQtGraph
    pg.setConfigOptions(antialias=True)
    pg.setConfigOption("background", "w")
    pg.setConfigOption("foreground", "k")

    window = PowerAnalyzer()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

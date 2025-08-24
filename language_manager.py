"""
Менеджер локализации для поддержки множественных языков
Автор: ADALM-PLUTO Power Analyzer
"""


class LanguageManager:
    """Менеджер локализации для поддержки множественных языков"""
    
    def __init__(self):
        self.current_language = "en"  # по умолчанию английский
        self.translations = self._load_translations()
    
    def _load_translations(self):
        """Загрузка всех переводов"""
        return {
            "ru": {
                # Заголовки окон и групп
                "window_title": "Анализатор мощности передатчика ADALM-PLUTO",
                "connection_group": "Подключение",
                "settings_group": "Настройки SDR",
                "presets_group": "Предустановки",
                "measurements_group": "Измерения",
                "status_group": "Статус",
                "log_group": "Лог",
                "detailed_log_group": "Детальный лог",
                "fft_group": "Спектр (FFT)",
                "rssi_group": "RSSI во времени",
                "power_group": "Пиковая мощность во времени",
                
                # Кнопки
                "connect_pluto": "Подключить PLUTO",
                "disconnect": "Отключить",
                "apply_settings": "Применить настройки",
                "auto_log": "Авто-лог",
                "clear_log": "Очистить",
                
                # Метки полей
                "frequency_mhz": "Частота (МГц):",
                "sample_rate_mhz": "Частота дискр. (МГц):",
                "bandwidth_mhz": "Полоса (МГц):",
                "gain_db": "Усиление (дБ):",
                "buffer_size": "Размер буфера:",
                "detection_threshold": "Порог обнар. (дБ):",
                "log_threshold": "Порог лога (дБ):",
                "log_interval": "Интервал лога (сек):",
                "channel_tolerance": "Допуск канала (кГц):",
                "language": "Язык:",
                
                # Измерения
                "rssi": "RSSI:",
                "peak_power": "Пиковая мощность:",
                "center_freq": "Центр. частота:",
                "dominant_freq": "Доминир. частота:",
                "freq_offset": "Смещение:",
                "log_count": "Записей:",
                
                # Статусы
                "not_connected": "Не подключено",
                "connecting": "Подключение...",
                "connected": "Подключено",
                "error": "Ошибка",
                "not_detected": "Не обнаружена",
                
                # Предустановки
                "lora_868": "LoRa 868 МГц",
                "wifi_2.4g": "WiFi 2.4 ГГц",
                "bluetooth": "Bluetooth",
                "868": "ISM 868 МГц",
                "915": "ISM 915 МГц",
                "fm_radio": "FM Радио",
                "gps_l1": "GPS L1",
                "lte_2100": "LTE 2100",
                
                # Подсказки
                "detection_tooltip": "Минимальная мощность для обнаружения сигнала",
                "log_tooltip": "Минимальная мощность сигнала для записи в лог",
                "interval_tooltip": "Минимальный интервал между записями одной частоты",
                "tolerance_tooltip": "Допуск для определения того же канала (±кГц)",
                "preset_tooltip": "Загрузить конфигурацию: {}",
                
                # Сообщения
                "pluto_connect_attempt": "Попытка подключения к ADALM-PLUTO...",
                "pluto_connected": "Успешно подключено к ADALM-PLUTO",
                "pluto_disconnected": "Отключено от ADALM-PLUTO",
                "settings_updated": "Настройки обновлены: {:.1f} МГц, {:.1f} Msps",
                "preset_loaded": "Загружена конфигурация: {}",
                "log_cleared": "Детальный лог и история частот очищены",
                "detection_threshold_changed": "Порог обнаружения изменен на {} дБ",
                "log_threshold_changed": "Порог логирования изменен на {} дБ",
                "log_interval_changed": "Интервал фильтра логирования изменен на {} сек",
                "tolerance_changed": "Допуск канала изменен на ±{} кГц",
                "detection_threshold_moved": "Порог обнаружения перемещен на {} дБ",
                "log_threshold_moved": "Порог логирования перемещен на {} дБ",
                "proportions_saved": "Пропорции: {:.1f}% / {:.1f}%",
                "language_changed": "Язык изменен на: {}",
                
                # Ошибки
                "error_prefix": "ОШИБКА: {}",
                "connection_error": "Ошибка подключения к PLUTO: {}",
                "settings_error": "Ошибка обновления настроек: {}",
                "data_error": "Ошибка получения данных: {}",
                
                # Оси графиков
                "power_axis": "Мощность",
                "frequency_axis": "Частота",
                "time_axis": "Время",
                "db_unit": "дБ",
                "hz_unit": "Гц",
                "dbm_unit": "дБм",
                "sec_unit": "с",
                "spectrum_legend": "Спектр",
                
                # Подписи линий на графике
                "detection_line_label": "Детекция",
                "log_line_label": "Лог",
            },
            
            "en": {
                # Window titles and groups
                "window_title": "ADALM-PLUTO Transmitter Power Analyzer",
                "connection_group": "Connection",
                "settings_group": "SDR Settings",
                "presets_group": "Presets",
                "measurements_group": "Measurements",
                "status_group": "Status",
                "log_group": "Log",
                "detailed_log_group": "Detailed Log",
                "fft_group": "Spectrum (FFT)",
                "rssi_group": "RSSI over Time",
                "power_group": "Peak Power over Time",
                
                # Buttons
                "connect_pluto": "Connect PLUTO",
                "disconnect": "Disconnect",
                "apply_settings": "Apply Settings",
                "auto_log": "Auto-Log",
                "clear_log": "Clear",
                
                # Field labels
                "frequency_mhz": "Frequency (MHz):",
                "sample_rate_mhz": "Sample Rate (MHz):",
                "bandwidth_mhz": "Bandwidth (MHz):",
                "gain_db": "Gain (dB):",
                "buffer_size": "Buffer Size:",
                "detection_threshold": "Detection Thresh. (dB):",
                "log_threshold": "Log Thresh. (dB):",
                "log_interval": "Log Interval (sec):",
                "channel_tolerance": "Channel Tolerance (kHz):",
                "language": "Language:",
                
                # Measurements
                "rssi": "RSSI:",
                "peak_power": "Peak Power:",
                "center_freq": "Center Freq.:",
                "dominant_freq": "Dominant Freq.:",
                "freq_offset": "Offset:",
                "log_count": "Records:",
                
                # Statuses
                "not_connected": "Not Connected",
                "connecting": "Connecting...",
                "connected": "Connected",
                "error": "Error",
                "not_detected": "Not Detected",
                
                # Presets
                "lora_868": "LoRa 868 MHz",
                "wifi_2.4g": "WiFi 2.4 GHz",
                "bluetooth": "Bluetooth",
                "868": "ISM 868 MHz",
                "915": "ISM 915 MHz",
                "fm_radio": "FM Radio",
                "gps_l1": "GPS L1",
                "lte_2100": "LTE 2100",
                
                # Tooltips
                "detection_tooltip": "Minimum power for signal detection",
                "log_tooltip": "Minimum signal power for log recording",
                "interval_tooltip": "Minimum interval between same frequency records",
                "tolerance_tooltip": "Tolerance for same channel detection (±kHz)",
                "preset_tooltip": "Load configuration: {}",
                
                # Messages
                "pluto_connect_attempt": "Attempting to connect to ADALM-PLUTO...",
                "pluto_connected": "Successfully connected to ADALM-PLUTO",
                "pluto_disconnected": "Disconnected from ADALM-PLUTO",
                "settings_updated": "Settings updated: {:.1f} MHz, {:.1f} Msps",
                "preset_loaded": "Configuration loaded: {}",
                "log_cleared": "Detailed log and frequency history cleared",
                "detection_threshold_changed": "Detection threshold changed to {} dB",
                "log_threshold_changed": "Log threshold changed to {} dB",
                "log_interval_changed": "Log filter interval changed to {} sec",
                "tolerance_changed": "Channel tolerance changed to ±{} kHz",
                "detection_threshold_moved": "Detection threshold moved to {} dB",
                "log_threshold_moved": "Log threshold moved to {} dB",
                "proportions_saved": "Proportions: {:.1f}% / {:.1f}%",
                "language_changed": "Language changed to: {}",
                
                # Errors
                "error_prefix": "ERROR: {}",
                "connection_error": "PLUTO connection error: {}",
                "settings_error": "Settings update error: {}",
                "data_error": "Data acquisition error: {}",
                
                # Graph axes
                "power_axis": "Power",
                "frequency_axis": "Frequency",
                "time_axis": "Time",
                "db_unit": "dB",
                "hz_unit": "Hz",
                "dbm_unit": "dBm",
                "sec_unit": "s",
                "spectrum_legend": "Spectrum",
                
                # Line labels on graph
                "detection_line_label": "Detection",
                "log_line_label": "Log",
            },
            
            "de": {
                # Fenstertitel und Gruppen
                "window_title": "ADALM-PLUTO Sendeleistungsanalysator",
                "connection_group": "Verbindung",
                "settings_group": "SDR-Einstellungen",
                "presets_group": "Voreinstellungen",
                "measurements_group": "Messungen",
                "status_group": "Status",
                "log_group": "Protokoll",
                "detailed_log_group": "Detailprotokoll",
                "fft_group": "Spektrum (FFT)",
                "rssi_group": "RSSI über Zeit",
                "power_group": "Spitzenleistung über Zeit",
                
                # Schaltflächen
                "connect_pluto": "PLUTO verbinden",
                "disconnect": "Trennen",
                "apply_settings": "Einstellungen anwenden",
                "auto_log": "Auto-Protokoll",
                "clear_log": "Löschen",
                
                # Feldbezeichnungen
                "frequency_mhz": "Frequenz (MHz):",
                "sample_rate_mhz": "Abtastrate (MHz):",
                "bandwidth_mhz": "Bandbreite (MHz):",
                "gain_db": "Verstärkung (dB):",
                "buffer_size": "Puffergröße:",
                "detection_threshold": "Erkennungsschwelle (dB):",
                "log_threshold": "Protokollschwelle (dB):",
                "log_interval": "Protokollintervall (Sek):",
                "channel_tolerance": "Kanaltoleranz (kHz):",
                "language": "Sprache:",
                
                # Messungen
                "rssi": "RSSI:",
                "peak_power": "Spitzenleistung:",
                "center_freq": "Mittenfrequenz:",
                "dominant_freq": "Dominante Freq.:",
                "freq_offset": "Versatz:",
                "log_count": "Einträge:",
                
                # Status
                "not_connected": "Nicht verbunden",
                "connecting": "Verbindung wird hergestellt...",
                "connected": "Verbunden",
                "error": "Fehler",
                "not_detected": "Nicht erkannt",
                
                # Voreinstellungen
                "lora_868": "LoRa 868 MHz",
                "wifi_2.4g": "WiFi 2,4 GHz",
                "bluetooth": "Bluetooth",
                "868": "ISM 868 MHz",
                "915": "ISM 915 MHz",
                "fm_radio": "UKW-Radio",
                "gps_l1": "GPS L1",
                "lte_2100": "LTE 2100",
                
                # Tooltips
                "detection_tooltip": "Mindestleistung für Signalerkennung",
                "log_tooltip": "Mindest-Signalleistung für Protokollierung",
                "interval_tooltip": "Mindestintervall zwischen gleichen Frequenzeinträgen",
                "tolerance_tooltip": "Toleranz für gleiche Kanalerkennung (±kHz)",
                "preset_tooltip": "Konfiguration laden: {}",
                
                # Nachrichten
                "pluto_connect_attempt": "Versuche Verbindung zu ADALM-PLUTO...",
                "pluto_connected": "Erfolgreich mit ADALM-PLUTO verbunden",
                "pluto_disconnected": "Von ADALM-PLUTO getrennt",
                "settings_updated": "Einstellungen aktualisiert: {:.1f} MHz, {:.1f} Msps",
                "preset_loaded": "Konfiguration geladen: {}",
                "log_cleared": "Detailprotokoll und Frequenzverlauf gelöscht",
                "detection_threshold_changed": "Erkennungsschwelle geändert auf {} dB",
                "log_threshold_changed": "Protokollschwelle geändert auf {} dB",
                "log_interval_changed": "Protokollfilter-Intervall geändert auf {} Sek",
                "tolerance_changed": "Kanaltoleranz geändert auf ±{} kHz",
                "detection_threshold_moved": "Erkennungsschwelle verschoben auf {} dB",
                "log_threshold_moved": "Protokollschwelle verschoben auf {} dB",
                "proportions_saved": "Proportionen: {:.1f}% / {:.1f}%",
                "language_changed": "Sprache geändert auf: {}",
                
                # Fehler
                "error_prefix": "FEHLER: {}",
                "connection_error": "PLUTO-Verbindungsfehler: {}",
                "settings_error": "Einstellungs-Update-Fehler: {}",
                "data_error": "Datenerfassungsfehler: {}",
                
                # Diagrammachsen
                "power_axis": "Leistung",
                "frequency_axis": "Frequenz",
                "time_axis": "Zeit",
                "db_unit": "dB",
                "hz_unit": "Hz",
                "dbm_unit": "dBm",
                "sec_unit": "s",
                "spectrum_legend": "Spektrum",
                
                # Linienbeschriftungen im Diagramm
                "detection_line_label": "Erkennung",
                "log_line_label": "Protokoll",
            }
        }
    
    def set_language(self, language_code):
        """Установить текущий язык"""
        if language_code in self.translations:
            self.current_language = language_code
            return True
        return False
    
    def get_text(self, key, *args):
        """Получить переведенный текст"""
        translation = self.translations.get(self.current_language, {}).get(key, key)
        if args:
            try:
                return translation.format(*args)
            except:
                return translation
        return translation
    
    def get_available_languages(self):
        """Получить список доступных языков"""
        return {
            "ru": "Русский",
            "en": "English", 
            "de": "Deutsch"
        }

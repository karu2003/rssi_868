# ADALM-PLUTO Transmitter Power Analyzer

A comprehensive Software Defined Radio (SDR) power analyzer application for the ADALM-PLUTO device, featuring real-time spectrum analysis, signal detection, and multilingual support.

## Features

### 🌍 Multilingual Support
- **Russian** (Русский) - Default language
- **English** - Full translation  
- **German** (Deutsch) - Complete localization
- Real-time language switching without restart

### 📡 SDR Analysis Capabilities
- Real-time FFT spectrum visualization
- Interactive threshold controls with draggable lines
- Signal detection with configurable power thresholds
- Frequency offset tracking and measurement
- RSSI monitoring over time
- Peak power analysis with historical data

### 🎛️ Advanced Configuration
- **Dynamic Preset System**: Built-in configurations for:
  - LoRa 868 MHz
  - WiFi 2.4 GHz
  - Bluetooth
  - ISM 868/915 MHz bands
  - FM Radio
  - GPS L1
  - LTE 2100
- **Flexible SDR Settings**:
  - Frequency range: 70 MHz - 6 GHz
  - Sample rate: 0.5 - 56 MHz
  - Bandwidth: 0.2 - 56 MHz
  - Gain: 0 - 76 dB
  - Buffer sizes: 1024 - 8192 samples

### 📊 Data Logging & Analysis
- **Smart Frequency Logging**: Automatic detection and logging of dominant frequencies
- **Temporal Filtering**: Configurable intervals to prevent duplicate entries
- **Channel Tolerance**: Intelligent grouping of nearby frequencies
- **Real-time Statistics**: Live counters and measurement displays
- **Export-ready Format**: Structured log entries with timestamps

### 🖥️ User Interface
- **Responsive Layout**: Resizable panels with persistent proportions
- **Interactive Graphs**: Live FFT, RSSI, and power plots with PyQtGraph
- **Visual Indicators**: Color-coded thresholds and signal markers
- **Intuitive Controls**: Grouped settings with tooltips and validation

## Requirements

### Hardware
- **ADALM-PLUTO SDR** device
- USB connection to host computer
- Compatible antenna for target frequency range

### Software Dependencies
```bash
pip install PyQt5 pyqtgraph numpy adi
```

### System Requirements
- **Python 3.7+**
- **Linux/Windows/macOS** (tested on Linux)
- **USB drivers** for ADALM-PLUTO

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd rssi_868
   ```

2. **Set up virtual environment** (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install PyQt5 pyqtgraph numpy adi
   ```

4. **Connect ADALM-PLUTO** device to USB port

5. **Run the application**:
   ```bash
   python rssi_868.py
   ```

## Usage Guide

### Quick Start
1. **Launch** the application
2. **Select language** from the dropdown (top panel)
3. **Choose preset** or configure SDR settings manually
4. **Click "Connect PLUTO"** to establish device connection
5. **Monitor** real-time spectrum and adjust thresholds as needed

### Configuration Workflow
1. **SDR Settings**:
   - Set center frequency for your target signal
   - Adjust sample rate and bandwidth appropriately
   - Configure gain for optimal signal reception
   - Apply settings before or after connection

2. **Detection Thresholds**:
   - **Detection Threshold**: Minimum power for signal identification
   - **Log Threshold**: Minimum power for logging events
   - Drag threshold lines on spectrum plot for real-time adjustment

3. **Logging Configuration**:
   - **Log Interval**: Minimum time between same-frequency entries
   - **Channel Tolerance**: Frequency range for duplicate detection
   - Enable/disable auto-logging as needed

### Preset Configurations
The application includes optimized presets for common protocols:

| Preset | Frequency | Sample Rate | Bandwidth | Use Case |
|--------|-----------|-------------|-----------|----------|
| LoRa 868 MHz | 868.0 MHz | 1.0 MHz | 0.5 MHz | IoT communications |
| WiFi 2.4G | 2400.0 MHz | 20.0 MHz | 10.0 MHz | WiFi monitoring |
| Bluetooth | 2440.0 MHz | 10.0 MHz | 5.0 MHz | BLE analysis |
| ISM 868 | 868.0 MHz | 10.0 MHz | 5.0 MHz | General ISM band |
| ISM 915 | 915.0 MHz | 10.0 MHz | 26.0 MHz | US ISM band |
| FM Radio | 100.0 MHz | 5.0 MHz | 2.0 MHz | FM broadcast |
| GPS L1 | 1575.42 MHz | 10.0 MHz | 5.0 MHz | GPS signals |
| LTE 2100 | 2100.0 MHz | 30.0 MHz | 20.0 MHz | Cellular analysis |

## Architecture

### Modular Design
```
rssi_868/
├── rssi_868.py           # Main application and GUI
├── language_manager.py   # Internationalization module
├── README.md            # Documentation
└── .venv/               # Virtual environment
```

### Key Components
- **PowerAnalyzer**: Main GUI application class
- **PlutoThread**: SDR communication and signal processing
- **SDRConfig**: Centralized configuration management
- **LanguageManager**: Localization and translation system

### Signal Processing Pipeline
1. **Data Acquisition**: Raw IQ samples from ADALM-PLUTO
2. **FFT Processing**: Real-time spectrum computation
3. **Signal Detection**: Peak finding with configurable thresholds
4. **Frequency Analysis**: Dominant frequency identification
5. **Logging System**: Smart filtering and data persistence

## Technical Specifications

### Performance Metrics
- **Real-time Processing**: 50ms update intervals
- **Frequency Resolution**: Determined by sample rate and buffer size
- **Dynamic Range**: -100 to +200 dB display range
- **Memory Usage**: Circular buffers with 1000-point history

### Supported Formats
- **Frequency Units**: Hz, kHz, MHz (automatic scaling)
- **Power Units**: dB, dBm (context-dependent)
- **Time Format**: ISO timestamps with millisecond precision
- **Export Format**: Human-readable structured text

## Troubleshooting

### Common Issues

**Connection Problems**:
- Verify ADALM-PLUTO USB connection
- Check device drivers installation
- Ensure device is not used by other applications
- Try different USB port or cable

**Performance Issues**:
- Reduce buffer size for lower latency
- Decrease sample rate if processing lags
- Close unnecessary applications
- Check system resource usage

**Display Problems**:
- Adjust threshold ranges if signals not visible
- Verify frequency range covers target signals
- Check gain settings for signal level
- Ensure antenna connection and tuning

### Debug Mode
Enable detailed logging by modifying the log level in the application or running with verbose output for troubleshooting.

## Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Submit pull request

### Coding Standards
- **Python**: Follow PEP 8 style guidelines
- **Comments**: Use docstrings for all public methods
- **Localization**: Add translations for new text elements
- **Testing**: Include unit tests for new functionality

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Analog Devices** for the ADALM-PLUTO hardware platform
- **PyQt5 Community** for the excellent GUI framework
- **PyQtGraph** developers for high-performance plotting capabilities
- **ADI Python Library** maintainers for SDR integration support

## Version History

- **v1.0.0** - Initial release with full multilingual support
  - Complete SDR analyzer implementation
  - Three-language localization (RU/EN/DE)
  - Dynamic preset system
  - Interactive threshold controls
  - Modular architecture

---

**Note**: This application is designed for educational and research purposes. Ensure compliance with local regulations when monitoring radio frequencies in your region.

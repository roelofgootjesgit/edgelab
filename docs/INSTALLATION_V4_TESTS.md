# Installation Guide - V4 Backtest Tests

## 📦 Vereiste Packages

Voor het draaien van de backtest execution tests zijn de volgende packages nodig:

### Core Dependencies (voor backtest execution)

```bash
pip install yfinance pandas
```

### Volledige Dependencies (voor hele project)

Als je alle dependencies wilt installeren:

```bash
pip install -r requirements.txt
```

## ✅ Check of packages geïnstalleerd zijn

```bash
python -c "import yfinance; import pandas; print('All dependencies installed!')"
```

## 📋 Wat doet elk package?

### `yfinance` (versie 0.2.66)
- **Gebruik:** Download historische marktdata
- **Waar gebruikt:** `core/data_downloader.py`
- **Functie:** Haalt OHLCV data op van Yahoo Finance voor backtesting

### `pandas` (versie 2.3.3)
- **Gebruik:** Data manipulatie en analyse
- **Waar gebruikt:** Overal in het project
- **Functie:** DataFrames voor price data, indicators, etc.

## 🚀 Installatie Commando's

### Optie 1: Alleen test dependencies
```bash
pip install yfinance pandas
```

### Optie 2: Alle project dependencies
```bash
pip install -r requirements.txt
```

### Optie 3: Met virtual environment (aanbevolen)
```bash
# Maak virtual environment
python -m venv venv

# Activeer (Windows)
venv\Scripts\activate

# Activeer (Linux/Mac)
source venv/bin/activate

# Installeer dependencies
pip install -r requirements.txt
```

## ✅ Verificatie

Na installatie, test of alles werkt:

```bash
# Test module mappings
python tests/test_template_modules.py

# Test backend conversion
python tests/test_backend_conversion_v4.py

# Test backtest execution (vereist yfinance en pandas)
python tests/test_backtest_execution_v4.py
```

## ⚠️ Troubleshooting

### "ModuleNotFoundError: No module named 'yfinance'"
```bash
pip install yfinance
```

### "ModuleNotFoundError: No module named 'pandas'"
```bash
pip install pandas
```

### "pip: command not found"
- Installeer Python met pip
- Of gebruik: `python -m pip install yfinance pandas`

### Windows: "pip is not recognized"
```bash
python -m pip install yfinance pandas
```

## 📝 Notities

- **yfinance** en **pandas** staan al in `requirements.txt`
- Als je het hele project al hebt geïnstalleerd, zijn deze waarschijnlijk al aanwezig
- De backtest execution tests hebben alleen deze 2 packages nodig (naast standaard Python libraries)

## 🔍 Check huidige installatie

```bash
# Check yfinance
python -c "import yfinance; print(f'yfinance version: {yfinance.__version__}')"

# Check pandas
python -c "import pandas; print(f'pandas version: {pandas.__version__}')"
```




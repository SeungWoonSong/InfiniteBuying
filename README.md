# Infinite Buying Bot for Stock Trading

This project implements an "Infinite Buying" bot, executing continuous trades based on a set strategy. The bot provides notifications through Telegram, making it easier to monitor trading activity. It leverages `PyKis` for API interactions, allowing users to configure trading parameters and handle errors effectively.

## Table of Contents

- [Project Structure](#project-structure)
- [Features](#features)
- [Setup](#setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Tests](#tests)
- [File Descriptions](#file-descriptions)
- [Logging](#logging)
- [License](#license)

## Project Structure

- **main.py**: Entry point to start the bot.
- **trading_bot.py**: Core trading logic, including buy/sell functionality, daily reporting, and error handling.
- **notifications.py**: Sends Telegram notifications for trading actions, balance updates, and errors.
- **config.py**: Stores configuration details for bot settings.
- **models.py**: Defines data classes for managing trading state and stock balance.
- **utils.py**: Utility functions for logging, time retrieval, and price calculations.
- **test_send.py**, **test_trading_bot.py**, **test_notification.py**: Test files for different parts of the bot.

## Features

- **Automated Trading**: Execute orders based on predefined strategies.
- **Telegram Notifications**: Real-time notifications for trades, errors, and daily summaries.
- **Configurable Settings**: Easily adjustable parameters for trading and notifications.
- **Error Logging**: All operations are logged for easier debugging.

## Setup

### Prerequisites

1. Python 3.8+ is required.
2. Install necessary packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your environment variables in a `.env` file:
   ```plaintext
   TELEGRAM_BOT_TOKEN=<Your_Telegram_Bot_Token>
   TELEGRAM_MY_ID=<Your_Telegram_Chat_ID>
   ID=<Your_Trading_ID>
   ACCOUNT=<Your_Account>
   KIS_APPKEY=<Your_KIS_App_Key>
   KIS_SECRETKEY=<Your_KIS_Secret_Key>
   VIRTUAL_KIS_APPKEY=<Your_Virtual_KIS_App_Key>
   VIRTUAL_SECRETKEY=<Your_Virtual_KIS_Secret_Key>
   ```

### Running the Bot

To launch the bot, use:
```bash
python main.py
```

## Configuration

Edit `config.py` for personalized settings:
- **BotConfig**: Defines the symbol, number of divisions for capital, and log directory.
- **TradingConfig**: Adjusts trading parameters such as initial buy amount and thresholds.

## Usage

1. **First Buy Execution**: Executes an initial buy based on configuration.
2. **Normal Trading**: Purchases stocks based on conditions and thresholds.
3. **Daily Reporting**: Sends a daily summary of account status.
4. **Error Notifications**: Handles and logs errors, with Telegram alerts for critical issues.

## Tests

Run all tests to ensure functionality:
```bash
python -m unittest discover
```

### Test Descriptions

- **test_send.py**: Tests sending various notifications.
- **test_trading_bot.py**: Validates trading functionalities such as buying, selling, and error handling.
- **test_notification.py**: Tests the Telegram notification system.

## File Descriptions

### main.py

Initiates the bot with configurations for trading and notification. Loads environment variables and starts the bot’s main loop.

### trading_bot.py

Contains the main trading logic with buy, sell, and reporting functions.

### notifications.py

Manages Telegram notifications for trade updates, balance summaries, and error alerts.

### config.py

Stores bot and trading configuration classes using `dataclass`.

### models.py

Defines data models for trading states and balance details.

### utils.py

Utility functions for logging setup, time handling, and price calculations.

### test_send.py, test_trading_bot.py, test_notification.py

Unit tests for notifications and bot operations. `test_trading_bot.py` also includes mock objects for isolated testing.

## Logging

All logs are saved in the specified log directory, with each session generating a new log file. Logs include details on trades, errors, and bot operations, aiding in tracking and debugging.

## License

This project is licensed under the MIT License.

---

**Important**: Use this bot with caution, especially in live trading environments. Always test in a simulated setting before deploying to a live account.
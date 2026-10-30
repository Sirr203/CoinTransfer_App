# CoinTrans

CoinTrans is a 100% offline mobile application designed to optimize cash and coin payments at registers in Japan (convenience stores, supermarkets, restaurants, and vending machines). Built with Python and [Flet](https://flet.dev) (powered by Flutter), CoinTrans calculates the ideal combination of banknotes and coins to hand to the cashier to minimize coin clutter in your wallet.

---

## Features

- **Wallet Inventory**: Track your exact count of Japanese Yen denominations (¥10,000, ¥5,000, ¥1,000, ¥500, ¥100, ¥50, ¥10, ¥5, ¥1) with quick `+`/`-` steppers or direct numeric entry.
- **Smart Payment Suggestion**:
  - **Fast Mode (Default)**: Minimizes the total physical count of items handed over plus coins received back. Hand over exact coins when available, avoiding unnecessary change.
  - **Optimize Notes Mode (Coin Cleanup)**: Prioritizes shedding loose coins to trade them up for banknotes, lightening your physical wallet.
- **Visual Breakdown**: Color-coded summary cards highlighting the exact amount and denominations to **Give** (teal) and **Receive Back** (blue).
- **Payment History & Statistics**:
  - Automatically records confirmed payments (bill amount, paid denominations, change received, calculation mode, and wallet balance).
  - Monthly spending summary with payment counts.
  - One-tap **Undo** for the latest payment, accurately restoring your previous wallet balances.
  - Delete individual entries or clear all history.
- **Internationalization (i18n)**:
  - English (`en`), Japanese (`ja`), and Vietnamese (`vi`).
  - Seamless in-app language switching via the settings gear icon without requiring an app restart.
  - Automatic device locale detection on initial launch.
- **100% Offline & Private**: All data is stored locally in JSON files inside the app's sandboxed storage. No internet connection, accounts, or analytics required.
- **Clean Mobile UI**: Wrapped in `SafeArea` to respect device notches and gesture bars, featuring bottom navigation and a responsive teal palette.

---

## Screenshots

<!--
Placeholder for mobile screenshots:
- Wallet inventory tab
- Payment suggestion result (Hand Over & Change)
- Payment history and monthly summary
-->

| Wallet Screen | Payment Suggestion | Payment History |
| :---: | :---: | :---: |
| _(Screenshot: Wallet)_ | _(Screenshot: Pay Screen)_ | _(Screenshot: History)_ |

---

## Project Structure

```text
coin_app/
├── .github/
│   └── workflows/
│       └── build-apk.yml     # Automated Android APK build on push
├── .vscode/
│   └── settings.json         # Workspace editor configurations
├── assets/
│   └── icon.png              # Application launcher icon
├── src/
│   ├── assets/
│   │   └── icon.png          # Bundled asset copy
│   ├── core.py               # Payment algorithm & core data models
│   ├── history.py            # Payment history tracking & statistics
│   ├── i18n.py               # Localization tables (en, ja, vi) & helper
│   ├── main.py               # Flet mobile user interface & navigation
│   └── test_core.py          # Comprehensive unit tests
├── .gitignore                # Git ignore patterns
├── CHANGELOG.md              # Version release history
├── pyproject.toml            # Project metadata & Flet packaging options
└── README.md                 # Project documentation
```

---

## How the Algorithm Works

Cash registers in Japan give change using a greedy strategy (the fewest coins and bills possible). CoinTrans solves a bounded knapsack dynamic programming problem over the candidate payment amounts $S \ge \text{bill}$:

1. **Fast Mode (Default)**:
   - Evaluates combinations where total handed amount $S \ge \text{bill}$.
   - Minimizes:
     $$\text{Cost} = (\text{items handed} + \text{items received in change}) \times 10^5 + (S - \text{bill})$$
   - Results in quick transactions at the register without receiving unnecessary loose change.

2. **Optimize Notes Mode (Coin Cleanup)**:
   - Coins carry a higher weight penalty than banknotes ($W_{\text{coin}} = 10, W_{\text{note}} = 2, W_{\text{hand}} = 1$).
   - The algorithm searches for payments that leave the lightest post-transaction wallet weight, actively combining small coins to receive larger coins or banknotes back (e.g. paying ¥1,130 for a ¥630 bill to receive a single ¥500 coin back).

---

## Data Storage

Data is saved as JSON files in the platform application data directory (`FLET_APP_STORAGE_DATA`, falling back to the user home directory). All write operations use atomic writes (`.tmp` file followed by an atomic rename) wrapped in exception handlers to prevent data corruption.

- `wallet.json`: Map of denomination amounts to quantities currently in your wallet.
- `settings.json`: User preferences including `prefer_notes` (boolean) and `language` (`"en"`, `"ja"`, or `"vi"`).
- `history.json`: List of up to 500 recent transactions containing unique IDs, ISO timestamps, bill amounts, breakdowns, mode, and wallet balance.

---

## Running Locally

### Prerequisites
- Python 3.10, 3.11, or 3.12
- [Flet](https://pypi.org/project/flet/) version `0.28.3`

### Installation & Execution
```bash
# Clone the repository
git clone https://github.com/Sirr203/CoinTransfer_App.git
cd CoinTransfer_App

# Install dependencies
pip install "flet==0.28.3"

# Run the desktop version
flet run src/main.py
# Or run with Python directly
python src/main.py
```

---

## Running Tests

The test suite runs with standard Python and does not require external testing libraries:

```bash
# Run unit tests
python src/test_core.py

# Verify byte compilation across all source files
python -m compileall src
```

---

## Building Android APK via GitHub Actions

The repository includes a GitHub Actions CI workflow ([`.github/workflows/build-apk.yml`](.github/workflows/build-apk.yml)) configured to build standalone Android APKs on every push to the `main` branch.

1. Push your changes to the `main` branch on GitHub:
   ```bash
   git push origin main
   ```
2. Navigate to the **Actions** tab on your GitHub repository page.
3. Select the latest workflow run.
4. Once completed (green checkmark), scroll down to the **Artifacts** section at the bottom.
5. Download `cointrans-apk` (downloaded as a `.zip` archive).
6. Extract the `.zip` archive on your computer or Android device to retrieve the `app-release.apk` file and install it.

---

## Contributing & Translating

Contributions, bug reports, and suggestions are welcome!

To contribute translations:
1. Open `src/i18n.py`.
2. Add or update translation strings in the `TRANSLATIONS` dictionary.
3. Ensure every key and `{placeholder}` in `en` matches in all languages.
4. Run `python src/test_core.py` to verify that parity tests pass.
5. Submit a pull request.

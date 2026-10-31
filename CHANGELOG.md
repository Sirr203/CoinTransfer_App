# Changelog

All notable changes to the CoinTrans project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-10-31

### Added
- Excel export functionality (`.xlsx`) via pure-Python `src/export.py` using `XlsxWriter`.
- Three localized spreadsheet tabs:
  1. **Payments**: Complete ledger with real Excel dates, formatted currency, calculation mode, and coin breakdowns.
  2. **Details**: Tidy/long format designed for pivot tables (payment id, date, kind, denomination, count, subtotal).
  3. **Summary**: Monthly expenditure totals with average bills, plus denomination usage analysis (handed over vs received).
- Date range picker for exports: "All Time", "This Month", and "Last Month".
- Friendly empty-state handling when no records exist for a selected range.
- Post-export success dialog with file path display and direct "Open File" launcher button.
- Comprehensive unit tests verifying multi-sheet output, row counts, cell types, and arithmetic parity.
- MIT License file for open-source distribution.

### Changed
- Added `XlsxWriter==3.2.0` pure-Python dependency.
- Updated `.gitignore` to prevent exporting temporary `.xlsx` files into version control.
- Bumped project version to `0.4.0`.

## [0.3.0] - 2026-10-30

### Added
- Multi-language internationalization supporting English (`en`), Japanese (`ja`), and Vietnamese (`vi`).
- Instant in-app language picker via the settings gear icon in the Wallet screen.
- Payment history tab tracking all confirmed transactions with monthly statistics.
- Undo capability for the most recent payment, reversing exact coin breakdowns into the wallet.
- Single-entry deletion and full history clear with confirmation dialogs.
- Automatic device locale detection on first launch.
- Parity tests verifying all language dictionary keys and placeholders match.
- Unit tests for payment history, capping at 500 entries, and data corruption resilience.

### Changed
- Migrated entire codebase, comments, docstrings, tests, and documentation to English.
- Replaced Vietnamese text across the UI with localized strings from `src/i18n.py`.
- Bumped project version to `0.3.0`.

## [0.2.0] - 2026-10-25

### Added
- Modern user interface built with Flet `SafeArea` and bottom `NavigationBar`.
- Dual calculation modes: default fast mode (fewest items) and note-optimization mode (coin cleanup).
- Dedicated summary cards and color-coded result sections for handover amount and change.
- Custom application launcher icon (`assets/icon.png`).
- Build number auto-incrementing in GitHub Actions CI workflow.

## [0.1.0] - 2026-10-25

### Added
- Initial dynamic programming knapsack payment optimization algorithm.
- Local atomic JSON wallet persistence (`wallet.json`).
- Core unit test suite.
- GitHub Actions workflow for building Android APKs with Flutter and Flet.


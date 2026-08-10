# Panama Canal Management System 🚢

A modern, desktop-based maritime traffic management and financial tracking system designed to streamline vessel processing, fee calculations, and analytics for the Panama Canal.

## 🌟 Key Features

* 🔒 **Secure Authentication:** Protected login screen utilizing **SHA-256 password hashing**.
* 🛳️ **Vessel Categorization & Fee Engine:** Automated categorization based on Deadweight Tonnage (**DWT**) (Standard, Premium, Neo-Panamax) with safety validation rules for oversized or invalid inputs.
* 💾 **SQLite Database Integration:** Full persistent data storage for transit logs and dynamic tariff/pricing management (`vessel_rates`).
* 📊 **Analytics & Visualizations:** Built-in **Matplotlib** interactive bar chart illustrating revenue breakdown by vessel status.
* 🔍 **Search & Log History:** Real-time search by vessel name and full historical log inspection.
* 📁 **Data Export:** Instant **CSV report generation** formatted for Excel, including transit IDs, timestamps, vessel metrics, and fees.
* 💱 **Live Exchange Rate Integration:** Fetches live USD exchange rates from the **NBP API** (National Bank of Poland).
* ↩️ **Transaction Management:** Ability to undo the last transit entry or reset the entire database safely with confirmation prompts.
* 🌐 **Full English Localization:** UI, popups, database logs, and exported CSV headers translated into professional maritime English.

## 🛠️ Tech Stack

* **Language:** Python 3.x
* **GUI Framework:** Tkinter / Ttk
* **Database:** SQLite3
* **Data Visualization:** Matplotlib
* **Security:** `hashlib` (SHA-256)
* **Networking & Data:** `urllib.request`, `json`, `csv`, `os`

## 📁 Project Structure

```text
.
├── gui_app.py           # Main GUI application, event handlers, and core application flow
├── database.py          # SQLite database connection, queries, and CRUD operations
├── canal_management.db  # SQLite database file (auto-generated on first run)
└── README.md            # Project documentation

🚀 Getting Started

1. Prerequisites:

- Ensure you have Python 3.x installed on your system. You will also need the matplotlib library installed: "pip install matplotlib"

2. Running the Application:

- Clone this repository (or download the files): 1. "git clone [https://github.com/DevTopolewski/panama-canal-system.git](https://github.com/DevTopolewski/panama-canal-system.git)", 2. "cd panama-canal-system"

3. Launch the application:

- "python gui_app.py"

4. Default Login Credentials:

- Password: admin123

## Author
DevTopolewski - Initial work.

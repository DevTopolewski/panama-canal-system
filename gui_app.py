import os
import hashlib
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import urllib.request
import matplotlib.pyplot as plt
import json

# Import all necessary tools from our database module
from database import init_db, add_vessel, get_vessel_stats, search_vessels, get_all_vessels, delete_all_vessels, db_load_prices, db_update_price, export_to_csv, delete_last_entry, get_stats_by_status

# Load prices from the database
init_db()
prices = db_load_prices()

# --- ENCRYPTED PASSWORD (SHA-256 for the word 'admin123') ---
SECRET_HASH = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"

def check_login(event=None):
    # Get the entered password
    password = password_entry.get()
    
    # Encrypt the entered password to check if its "hash" matches ours
    hashed_input = hashlib.sha256(password.encode()).hexdigest()
    
    if hashed_input == SECRET_HASH:
        login_window.destroy()  # Close the small login window
        root.deiconify()        # Reveal the main application window
    else:
        messagebox.showerror("Access Denied", "🛑 Invalid password! Please try again.")
        password_entry.delete(0, tk.END)  # Clear the entry field after an error

# --- CATEGORIZATION LOGIC FUNCTION ---
def check_vessel_status(dwt: int) -> str:
    if dwt <= 0:
        return "ERROR_INVALID_VALUE"
    if dwt > 250000:
        return "REJECTED_OVERSIZE"
    if dwt > 60000:
        return "NEO-PANAMAX"
    elif dwt > 40000:
        return "PREMIUM"
    elif dwt > 10000:
        return "STANDARD"
    else:
        return "REJECTED"

# --- FINANCIAL LOGIC FUNCTION ---
def calculate_vessel_fee(dwt: int, category: str) -> int:
    # Base fee depending on category
    if category in ["REJECTED", "REJECTED_OVERSIZE", "ERROR_INVALID_VALUE"]:
        return 0
    return prices.get(category, 0)

# --- ANALYTICS CHART GENERATION FUNCTION ---
def show_analytics_chart():
    # Fetch aggregated data from the database
    stats = get_stats_by_status()
    
    if not stats:
        messagebox.showwarning("No Data", "The database is empty! Add some vessels first.")
        return

    # Separate the results into two lists: statuses and total fees
    statuses = [row[0] for row in stats]
    fees = [row[1] for row in stats]

    # Create a new chart window
    plt.figure(figsize=(7, 5))
    
    # Draw a bar chart with nice colors
    colors = ['#2ecc71', '#3498db', '#e74c3c', '#f1c40f']
    bars = plt.bar(statuses, fees, color=colors[:len(statuses)])
    
    # Title and axis labels
    plt.title("Total Revenue by Vessel Status ($)", fontsize=12, fontweight='bold')
    plt.xlabel("Vessel Status", fontsize=10)
    plt.ylabel("Total Fees ($)", fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.5) # Subtle grid

    # Add values above each bar
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, f"${yval:,}", ha='center', va='bottom', fontweight='bold')

    # Display the chart window
    plt.tight_layout()
    plt.show()

# --- DASHBOARD UPDATE FUNCTION (SQL VERSION) ---
def update_dashboard():
    # Fetch ready calculations straight from the database engine
    total_ships, total_earnings = get_vessel_stats()
    stats_label.config(text=f"Processed Vessels: {total_ships}   |   Total Revenue: ${total_earnings:,}")

# --- LOG SEARCH FUNCTION (SQL VERSION) ---
def search_vessel():
    query = search_entry.get().strip()
    if not query:
        messagebox.showwarning("Empty Search", "Enter a vessel name to search!")
        return
    
    # Clear the results window
    search_results_box.config(state="normal")
    search_results_box.delete("1.0", tk.END)
    
    # Fetch search results from the database
    rows = search_vessels(query)
                
    if rows:
        for row in rows:
            timestamp, name, dwt, status, fee = row
            # Format the text professionally!
            entry_text = f"[{timestamp}] | Vessel: {name:<10} | DWT: {dwt:<7} | Status: {status:<19} | Fee: ${fee:>10,}\n\n"
            search_results_box.insert(tk.END, entry_text)
    else:
        search_results_box.insert(tk.END, f"No vessel found with name: '{query}'")
        
    search_results_box.config(state="disabled")

# --- PROCESSING FUNCTION ---
def process_ship():
    name = name_entry.get()
    dwt_raw = dwt_entry.get()
    
    if not name or not dwt_raw:
        messagebox.showwarning("Missing Data", "Please fill in both fields!")
        return
        
    try:
        dwt = int(dwt_raw)
        if dwt <= 0:
            messagebox.showerror("Data Error", "Vessel displacement must be greater than 0!")
            return
        status = check_vessel_status(dwt)
        fee = calculate_vessel_fee(dwt, status)
        
        if "REJECTED" in status or "ERROR" in status:
            result_color = "#cc0000"
        else:
            result_color = "#006600"
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            add_vessel(now_str, name, dwt, status, fee)
            # Automatically refresh the dashboard counter after adding a vessel!
            update_dashboard()
            # Clear fields after successful save!
            name_entry.delete(0, tk.END)
            dwt_entry.delete(0, tk.END)
        
        result_label.config(
            text=f"VESSEL: {name}\nSTATUS: {status}\nFEE: ${fee:,}", 
            fg=result_color
        )
        
    except ValueError:
        messagebox.showerror("Weight Error", "DWT must be an integer!")

# --- UNDO LAST ADDED VESSEL ---
def undo_last_ship():
    # Ask the user to confirm deletion (protection against accidental clicks)
    confirm = messagebox.askyesno("Confirmation", "Are you sure you want to delete the LAST added vessel from the database?")
    
    if confirm:
        # Assuming the database module is imported
        success = delete_last_entry()
        
        if success:
            # If deleted, refresh the dashboard!
            update_dashboard()
            messagebox.showinfo("Success", "The last vessel was successfully removed from the system.")
        else:
            messagebox.showwarning("No Data", "Database is empty, nothing to undo!")

# --- SHOW FULL HISTORY ---
def show_all_vessels():
    search_results_box.config(state="normal")
    search_results_box.delete("1.0", tk.END)

    rows = get_all_vessels()

    if rows:
        for row in rows:
            timestamp, name, dwt, status, fee = row
            entry_text = f"[{timestamp}] | Vessel: {name:<10} | DWT: {dwt:<7} | Status: {status:<19} | Fee: ${fee:>10,}\n\n"
            search_results_box.insert(tk.END, entry_text)
    else:
        search_results_box.insert(tk.END, "Database is empty. Add some vessels!")

    search_results_box.config(state="disabled")

# --- RESET DATABASE WITH CONFIRMATION ---
def reset_database():
    # Popup window with Yes/No question
    confirm = messagebox.askyesno("⚠️ CONFIRMATION", "Are you sure you want to PERMANENTLY delete the entire vessel history?")

    if confirm: # If user clicked YES
        delete_all_vessels()     # Clear the SQL database
        update_dashboard()       # Reset dashboard statistics

        # Clear and disable the search results box
        search_results_box.config(state="normal")
        search_results_box.delete("1.0", tk.END)
        search_results_box.insert(tk.END, "Database has been reset.")
        search_results_box.config(state="disabled")

        messagebox.showinfo("Success", "Database successfully cleared!")

def handle_save_rates():
    global prices
    try:
        new_standard = int(rate_standard_entry.get())
        new_premium = int(rate_premium_entry.get())
        new_neo = int(rate_neo_entry.get())
        
        if new_standard <= 0 or new_premium <= 0 or new_neo <= 0:
            messagebox.showerror("Error", "Rates must be greater than 0!")
            return
            
        # Save values directly to SQLite
        db_update_price("STANDARD", new_standard)
        db_update_price("PREMIUM", new_premium)
        db_update_price("NEO-PANAMAX", new_neo)
        
        # Reload the dictionary on the fly from the database
        prices = db_load_prices()
        
        messagebox.showinfo("Success", "Rates updated successfully in the SQL database!")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid integers!")

def update_clock():
    # Get current date and time in a nice YYYY-MM-DD HH:MM:SS format
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Update text in our label
    time_label.config(text=f"{current_time}")
    # 🔥 MAGIC: ask Tkinter to run this function again in 1 second
    root.after(1000, update_clock)

def download_rate_usd():
    url = "http://api.nbp.pl/api/exchangerates/rates/a/usd/?format=json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data['rates'][0]['mid']
    except Exception:
        return None

def trigger_export():
    try:
        report_file = export_to_csv()
        messagebox.showinfo(
            "Report Generated", 
            f"🚀 Success!\n\nCanal statistics saved to Excel/CSV file.\n\nLocation:\n{report_file}"
        )
    except Exception as e:
        # In case of any issues, the program won't crash, just show an error
        messagebox.showerror("Export Error", f"Something went wrong while saving the file:\n{e}")

# --- MAIN WINDOW CREATION ---
root = tk.Tk()
root.title("PCS v2.4")
root.geometry("400x850")

BG_COLOR = "#003366"   
TEXT_COLOR = "#FFFFFF" 
root.configure(bg=BG_COLOR)

# --- BUTTON STYLE CONFIGURATION ---
style = ttk.Style()
style.theme_use('clam')  # Forcing 'clam' theme for consistent look

# Creating a custom style for our buttons
style.configure(
    "Custom.TButton",
    background="#005588",      # Marine blue background
    foreground="#FFFFFF",      # White text
    font=("Arial", 11, "bold"),
    borderwidth=0,
    focuscolor="none"          # Removes white flickering on Mac
)

# Defining hover behavior
style.map("Custom.TButton",
    background=[("active", "#004477")]  # Darker blue on hover
)

# HIDE main window on startup
root.withdraw() 

# --- CREATE LOGIN WINDOW ---
login_window = tk.Toplevel(root)
login_window.title("PCS v2.4")
login_window.geometry("300x200")
login_window.configure(bg="#003366")
login_window.resizable(False, False)

tk.Label(
    login_window, 
    text="LOGIN 🔒", 
    font=("Arial", 16, "bold"), 
    bg="#003366", 
    fg="white"
).pack(pady=20)

# Password entry (show="*" hides characters)
password_entry = tk.Entry(login_window, show="*", font=("Arial", 14), bg="#F0F0F0", fg="#000000", justify="center", width=15)
password_entry.pack(pady=10)
# Allows login by pressing the ENTER key
password_entry.bind("<Return>", check_login) 

login_button = ttk.Button(
    login_window, 
    text="Sign In 🔐", 
    command=check_login, 
    style="Custom.TButton"
)
login_button.pack(pady=15)

# --- SECTION 1: BLACK STATISTICS DASHBOARD ---
stats_frame = tk.Frame(root, bg="#000000", height=40)
stats_frame.pack(fill="x", side="top")

stats_label = tk.Label(stats_frame, text="Loading...", font=("Arial", 11, "bold"), bg="#000000", fg="#FFFFFF")
stats_label.pack(pady=10)

# --- SECTION 2: DYNAMIC SYSTEM CLOCK & API ---
# Create a small frame under the black dashboard
time_frame = tk.Frame(root, bg=BG_COLOR)
time_frame.pack(fill="x", side="top", pady=5)

time_label = tk.Label(time_frame, text="", font=("Arial", 10, "bold"), bg=BG_COLOR, fg="#555555")
time_label.pack()

# USD Rate from NBP API
usd_label = tk.Label(time_frame, text="💵 Fetching USD exchange rate...", font=("Arial", 9, "italic"), bg=BG_COLOR, fg="#2980b9")
usd_label.pack(pady=(2, 0))

# Start the clock
update_clock()

# 🚀 FETCH NBP API RATE ON STARTUP:
aktualny_kurs = download_rate_usd()
if aktualny_kurs:
    usd_label.config(text=f"💵 USD Rate (NBP): {aktualny_kurs} PLN", font=("Arial", 9, "bold"), fg="#27ae60")
else:
    usd_label.config(text="💵 USD Rate: Network Error", fg="#c0392b")

# --- SECTION 3: VESSEL PROCESSING ---
title = tk.Label(root, text="Panama Canal System", font=("Arial", 14, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
title.pack(pady=15)

name_label = tk.Label(root, text="Vessel Name:", font=("Arial", 11, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
name_label.pack(pady=2)
name_entry = tk.Entry(root, width=25, font=("Arial", 12), bg="#F0F0F0", fg="#000000", insertbackground="black")
name_entry.pack(pady=5)

dwt_label = tk.Label(root, text="Displacement (DWT):", font=("Arial", 11, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
dwt_label.pack(pady=2)
dwt_entry = tk.Entry(root, width=25, font=("Arial", 12), bg="#F0F0F0", fg="#000000", insertbackground="black")
dwt_entry.pack(pady=5)

calc_button = ttk.Button(root, text="Process Transit 🚢", command=process_ship, style="Custom.TButton")
calc_button.pack(pady=15)

result_label = tk.Label(root, text="Enter data and click the button above.", font=("Courier", 11, "bold"), bg=BG_COLOR, fg="#000000", justify="left")
result_label.pack(pady=10)

action_buttons_frame = tk.Frame(root, bg=BG_COLOR)
action_buttons_frame.pack(pady=15)

undo_button = ttk.Button(
    action_buttons_frame, 
    text="Undo Last Vessel ↩️", 
    command=undo_last_ship, 
    style="Custom.TButton"
)
undo_button.pack(side="left", padx=10) 

chart_button = ttk.Button(
    action_buttons_frame, 
    text="Generate Analytics Chart 📊", 
    command=show_analytics_chart, 
    style="Custom.TButton"
)
chart_button.pack(side="left", padx=10)

# --- SYSTEM DIVIDER ---
separator = tk.Frame(root, height=2, bd=1, relief="sunken", bg="#000000")
separator.pack(fill="x", padx=20, pady=10)

# --- SECTION 4: SQL LOG SEARCH ---
search_title = tk.Label(root, text="SQL Log Search", font=("Arial", 12, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
search_title.pack(pady=5)

search_entry = tk.Entry(root, width=25, font=("Arial", 12), bg="#F0F0F0", fg="#000000", insertbackground="black")
search_entry.pack(pady=5)

search_button = ttk.Button(root, text="Search Database 🔍", command=search_vessel, style="Custom.TButton")
search_button.pack(pady=5)

show_all_button = ttk.Button(root, text="Show Full History 📜", command=show_all_vessels, style="Custom.TButton")
show_all_button.pack(pady=2)

search_results_box = tk.Text(root, width=45, height=5, font=("Courier", 10), bg="#F0F0F0", fg="#000000", state="disabled")
search_results_box.pack(pady=10, padx=15)

reset_button = ttk.Button(root, text="Reset Database ⚠️", command=reset_database, style="Custom.TButton")
reset_button.pack(pady=10)

# --- SECTION 5: BUSINESS REPORTS EXPORT ---
export_button = ttk.Button(root, text="Generate Operational Report (CSV) 📥", command=trigger_export, style="Custom.TButton")
export_button.pack(pady=10)

# --- SYSTEM DIVIDER ---
separator = tk.Frame(root, height=2, bd=1, relief="sunken", bg="#000000")
separator.pack(fill="x", padx=20, pady=10)

# --- SECTION 6: RATE CONFIGURATION ---
rates_label = tk.Label(root, text="SQL Rate Configuration ($)", font=("Arial", 11, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
rates_label.pack(pady=5)

rates_frame = tk.Frame(root, bg=BG_COLOR)
rates_frame.pack(pady=5)

# STANDARD Field
tk.Label(rates_frame, text="Std:", bg=BG_COLOR, fg=TEXT_COLOR, font=("Arial", 10, "bold")).grid(row=0, column=0, padx=2)
rate_standard_entry = tk.Entry(rates_frame, width=6, font=("Arial", 10))
rate_standard_entry.insert(0, str(prices.get("STANDARD", 5000)))
rate_standard_entry.grid(row=0, column=1, padx=4)

# PREMIUM Field
tk.Label(rates_frame, text="Prem:", bg=BG_COLOR, fg=TEXT_COLOR, font=("Arial", 10, "bold")).grid(row=0, column=2, padx=2)
rate_premium_entry = tk.Entry(rates_frame, width=6, font=("Arial", 10))
rate_premium_entry.insert(0, str(prices.get("PREMIUM", 12000)))
rate_premium_entry.grid(row=0, column=3, padx=4)

# NEO-PANAMAX Field
tk.Label(rates_frame, text="Neo:", bg=BG_COLOR, fg=TEXT_COLOR, font=("Arial", 10, "bold")).grid(row=0, column=4, padx=2)
rate_neo_entry = tk.Entry(rates_frame, width=6, font=("Arial", 10))
rate_neo_entry.insert(0, str(prices.get("NEO-PANAMAX", 25000)))
rate_neo_entry.grid(row=0, column=5, padx=4)

# Save Button (ttk)
save_rates_button = ttk.Button(root, text="Save Rates to SQL 💾", command=handle_save_rates, style="Custom.TButton")
save_rates_button.pack(pady=5)

# Run initial dashboard update from the database on startup!
update_dashboard()

root.mainloop()

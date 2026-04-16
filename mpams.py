# We need this so we can work with JSON files
import json
from datetime import datetime, timedelta

# We need this to check if the file already exists
import os
# Importing Pandas for DataFrame functionality
import pandas as pd

def load_data_as_df(filename='data.json'):
    data = load_data(filename)  # reuse your existing load_data()
    if not data:
        print("No data found.")
        return pd.DataFrame()  # empty DataFrame
    return pd.DataFrame(data)

# A function to generate attendance summary
def attendance_summary():
    df = load_data_as_df()
    if df.empty:
        print("No attendance records found.")
        return

    # Ensure we have a session_date for reporting
    if 'session_date' not in df.columns:
        df['session_date'] = pd.to_datetime(datetime.now().date())
    else:
        df['session_date'] = pd.to_datetime(df['session_date'], errors='coerce')

    df['raw_date'] = df['session_date'].dt.date

    # per-student metrics
    by_status = df.groupby('name')['status'].value_counts().unstack(fill_value=0)
    present = by_status.get('Present', pd.Series(0, index=by_status.index))
    absent = by_status.get('Absent', pd.Series(0, index=by_status.index))
    total = present + absent
    percentage = (present / total * 100).fillna(0)

    print("\n--- Attendance Metrics (all time) ---")
    for name in total.index:
        print(f"{name}: Present={present[name]}, Absent={absent[name]}, Percentage={percentage[name]:.1f}%")

    # Period-based reports
    today = datetime.now().date()
    week_start = today - timedelta(days=6)
    month_start = today - timedelta(days=29)

    week_df = df[(df['raw_date'] >= week_start) & (df['raw_date'] <= today)]
    month_df = df[(df['raw_date'] >= month_start) & (df['raw_date'] <= today)]

    def report_period(label, p_df):
        print(f"\n--- {label} Report ({p_df.shape[0]} records) ---")
        if p_df.empty:
            print("No records in this period.")
            return
        p_stats = p_df.groupby('name')['status'].value_counts().unstack(fill_value=0)
        p_present = p_stats.get('Present', pd.Series(0, index=p_stats.index))
        p_absent = p_stats.get('Absent', pd.Series(0, index=p_stats.index))
        for name in p_stats.index:
            p_total = p_present[name] + p_absent[name]
            p_percent = (p_present[name] / p_total * 100) if p_total else 0
            print(f"{name}: Present={p_present[name]}, Absent={p_absent[name]}, Percentage={p_percent:.1f}%")

    report_period('Weekly', week_df)
    report_period('Monthly', month_df)

    # Frequent absentees
    abs_counts = absent.sort_values(ascending=False)
    top_absentees = abs_counts[abs_counts > 0].head(5)
    print("\n--- Frequent Absentees ---")
    if top_absentees.empty:
        print("No absentees found.")
    else:
        for name, count in top_absentees.items():
            print(f"{name}: {count} absent days")

# A function to export the attendance report to Excel
def export_report_excel(filename):
    # Ensure .xlsx extension is present
    if not filename.lower().endswith('.xlsx'):
        filename = f"{filename}.xlsx"

    df = load_data_as_df()
    if df.empty:
        print("No data to export.")
        return
    
    # Export to Excel
    df.to_excel(filename, index=False)
    print(f"Report saved as {filename}")

# -----------------------------
# FUNCTION: LOAD DATA
# -----------------------------
# This function reads the data from the JSON file.
# If the file does not exist yet, it will return an empty list.
def load_data(filename='data.json'):
    
    # Check if the file already exists
    if not os.path.exists(filename):
        # If the file is not found, return an empty list
        # (This means there are no users saved yet)
        return []
    
    # Open the file in READ mode ('r')
    with open(filename, 'r') as file:
        # Convert the JSON file content into Python data
        # and return it
        return json.load(file)


# -----------------------------
# FUNCTION: SAVE DATA
# -----------------------------
# This function saves the updated list of users
# into the JSON file.
def save_data(data, filename='data.json'):
    
    # Open the file in WRITE mode ('w')
    # This will overwrite the old data
    with open(filename, 'w') as file:
        
        # Convert Python data into JSON format
        # indent=4 makes the file easier to read
        json.dump(data, file, indent=4)


# -----------------------------
# CREATE ENTRY
# -----------------------------
# This function adds a new entry to the file.
def new_entry(new_entry):
    
    # Load existing users
    data = load_data()

    # Automatically add session_date and timing metadata
    now = datetime.now()
    new_entry["session_date"] = now.date().isoformat()  # YYYY-MM-DD
    new_entry["created_at"] = now.isoformat(sep=' ', timespec='seconds')
    new_entry["updated_at"] = new_entry["created_at"]

    # Add the new user to the list
    data.append(new_entry)
    
    # Save the updated list back to the file
    save_data(data)
    
    print("Entry added successfully!")


# -----------------------------
# READ ENTRIES
# -----------------------------
# This function displays all entries saved in the file.
def read_entries():
    
    # Load existing entries
    data = load_data()
    
    # If there are no entries
    if not data:
        print("No entries found.")
        return
    
    # Loop through each entry and print it
    for entry in data:
        print(entry)


# -----------------------------
# UPDATE ENTRY
# -----------------------------
# This function updates the information of an entry
# based on their ID number.
def update_entry(entry_id, updated_info):
    
    # Load existing entries
    data = load_data()
    
    # Loop through each entry
    for entry in data:
        
        # Check if the ID matches
        if entry['id'] == entry_id:
            
            # Update the entry's information
            entry.update(updated_info)
            
            # Update timestamp for tracking modifications
            entry['updated_at'] = datetime.now().isoformat(sep=' ', timespec='seconds')
            
            # Save the updated data
            save_data(data)
            
            print("Entry updated successfully!")
            return
    
    # If no matching ID was found
    print("Entry not found.")


# -----------------------------
# DELETE ENTRY
# -----------------------------
# This function removes an entry based on their ID.
def delete_entry(entry_id):
    
    # Load existing entries
    data = load_data()
    
    # Create a new list that EXCLUDES the entry with the given ID
    new_data = [entry for entry in data if entry['id'] != entry_id]
    
    # If no entry was removed
    if len(new_data) == len(data):
        print("Entry not found.")
    else:
        # Save the updated list
        save_data(new_data)
        print("Entry deleted successfully!")


# -----------------------------
# MPAMS (Multi Purpose Attendance Monitoring System)
# -----------------------------
if __name__ == "__main__":
    print("WELCOME TO MPAMS! (Multi Purpose Attendance Monitoring System)")
    print("Made by: Mc Lawrence Castillo\n" 
          "(This serves as my Quarter Project this 4th quarter.)")

    # The main loop of the program. It will keep running until the user decides to exit.
    a=1
    while a==1:

        print("Do you wish to?\n"
          "1. Add a new entry\n"
          "2. View all entries\n"
          "3. Update an entry\n"
          "4. Delete an entry\n"
          "5. View attendance summary\n"
          "6. Export report to Excel\n"
          "7. Exit the program")
        
        choice = input("Enter your choice (1-7): ")

        # If user inputs 1, we will add a new entry
        if choice == '1':
            IDinput = input("Enter ID: ")
            LNinput = input("Enter Last Name: ")
            FNinput = input("Enter First Name: ")
            MNinput = input("Enter Middle Name: ")
            statusinput = input("Enter Status (P for Present, A for Absent): ")
            
            if statusinput not in ("P", "A"):
                print("Invalid input for Status. Please enter 'P' for Present or 'A' for Absent.")
                statusinput = input("Enter Status (P for Present, A for Absent): ")
            if statusinput in ("P", "A"):
                new_entry({
                    "id": IDinput,
                    "name": f"{LNinput}, {FNinput} {MNinput}",
                    "status": "Present" if statusinput == "P" else "Absent"
                })
                print("Sucessfully added entry! Do you want to continue? (1 for Yes, 0 for No)")
                a = int(input())

        # If user inputs 2, we will display all entries
        elif choice == '2':
            read_entries()
            print("Do you wish to view the entries again? (1 for Yes, 0 for No)")
            a = int(input())

        # If user inputs 3, we will update an entry
        elif choice == '3':
            desicion = input("What do you want to update? (1 for Name, 2 for Status, 3 for Date): ")

            if desicion == '1':
                IDinput = input("Enter the ID of the entry you want to update: ")
                LNinput = input("Enter the new Last Name: ")
                FNinput = input("Enter the new First Name: ")
                MNinput = input("Enter the new Middle Name: ")
                update_entry(IDinput, {"name": f"{LNinput}, {FNinput} {MNinput}"})
                print("Entry update successful! Do you wish to update another entry? (1 for Yes, 0 for No)")
                a = int(input())

            elif desicion == '2':
                IDinput = input("Enter the ID of the entry you want to update: ")
                statusinput = input("Enter the new Status (P for Present, A for Absent): ")
                if statusinput not in ("P", "A"):
                    print("Invalid input for Status. Please enter 'P' for Present or 'A' for Absent.")
                    statusinput = input("Enter the new Status (P for Present, A for Absent): ")
                if statusinput in ("P", "A"):
                    update_entry(IDinput, {"status": "Present" if statusinput == "P" else "Absent"})
                    print("Entry update successful! Do you wish to update another entry? (1 for Yes, 0 for No)")
                    a = int(input())

            elif desicion == '3':
                IDinput = input("Enter the ID of the entry you want to update: ")
                dateinput = input("Enter the new session date (YYYY-MM-DD): ")
                update_entry(IDinput, {"session_date": dateinput})
                print("Entry date update successful! Do you wish to update another entry? (1 for Yes, 0 for No)")
                a = int(input())

            else:
                print("Invalid selection for update mode.")
                a = 1

        elif choice == '4':
            IDinput = input("Enter the ID of the entry you want to delete: ")
            delete_entry(IDinput)
            print("Entry deleted successfully! Do you wish to delete another entry? (1 for Yes, 0 for No)")
            a = int(input())

        elif choice == '5':
            attendance_summary()
            print("Do you wish to view the attendance summary again? (1 for Yes, 0 for No)")
            a = int(input())

        elif choice == '6':
            filename = input("Enter the filename for the Excel report: ")
            export_report_excel(filename)
            print(f"Export successful! The file was saved as ({filename}) in the same folder as this program.")
            print("Do you wish to export the report again? (1 for Yes, 0 for No)")
            a = int(input())

        elif choice == '7':
            print("Exiting the program. Goodbye!")
            a = 0

        else:
            print("Invalid choice. Please enter a number between 1 and 7.")
            print("Do you wish to try again? (1 for Yes, 0 for No)")
            a = int(input())
       

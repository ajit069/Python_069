
FILE_NAME = "electricity_data.txt"

consumption = {}


def add_consumption():
    month = input("Enter month name: ").strip().title()

    if month == "":
        print("Month name cannot be empty.")
        return

    if month in consumption:
        print("Record for this month already exists.")
        return

    try:
        units = float(input("Enter electricity consumption (units): "))

        if units < 0:
            print("Consumption cannot be negative.")
        else:
            consumption[month] = units
            print("Consumption record added successfully.")

    except ValueError:
        print("Invalid input! Please enter a numeric value.")


def view_records():
    if not consumption:
        print("No consumption records available.")
        return

    print("\n========== ELECTRICITY RECORDS ==========")
    print("{:<18}{}".format("Month", "Consumption (units)"))
    print("-----------------------------------------")

    for month, units in consumption.items():
        print("{:<18}{:.2f}".format(month, units))

    print("=========================================")



def calculate_total():
    if not consumption:
        print("No records available.")
        return

    total = sum(consumption.values())
    print("Total Consumption:", round(total, 2), "units")



def calculate_average():
    if not consumption:
        print("No records available.")
        return

    average = sum(consumption.values()) / len(consumption)
    print("Average Consumption:", round(average, 2), "units")


def find_highest_lowest():
    if not consumption:
        print("No records available.")
        return

    highest_month = max(consumption, key=consumption.get)
    lowest_month = min(consumption, key=consumption.get)

    print("Highest Consumption:")
    print(highest_month, "-", consumption[highest_month], "units")

    print("\nLowest Consumption:")
    print(lowest_month, "-", consumption[lowest_month], "units")


def forecast_consumption():
    if len(consumption) < 3:
        print("Please add at least 3 monthly records for forecasting.")
        return

    last_three = list(consumption.values())[-3:]
    forecast = sum(last_three) / 3

    print("\n========== CONSUMPTION FORECAST ==========")
    print("Last 3 months consumption:", last_three)
    print("Forecast for next month:", round(forecast, 2), "units")
    print("Method: 3-month moving average")
    print("==========================================")


def save_records():
    try:
        with open(FILE_NAME, "w") as file:
            for month, units in consumption.items():
                file.write(month + "," + str(units) + "\n")

        print("Records saved successfully in", FILE_NAME)

    except OSError:
        print("Unable to save the records.")


def load_records():
    try:
        with open(FILE_NAME, "r") as file:
            for line in file:
                line = line.strip()

                if line == "":
                    continue

                try:
                    month, units = line.split(",")
                    consumption[month] = float(units)
                except ValueError:
                    print("Skipping an invalid record in the data file.")

        print("Records loaded successfully.")

    except FileNotFoundError:
        print("No previous data file found. Starting with empty records.")

    except OSError:
        print("Unable to read the data file.")


def main():
    load_records()

    while True:
        print("\n============================================")
        print(" ELECTRICITY CONSUMPTION ANALYSIS SYSTEM")
        print("============================================")
        print("1. Add Monthly Consumption")
        print("2. View Consumption Records")
        print("3. Calculate Total Consumption")
        print("4. Calculate Average Consumption")
        print("5. Find Highest and Lowest Consumption")
        print("6. Forecast Next Month Consumption")
        print("7. Save Records")
        print("8. Exit")
        print("============================================")

        choice = input("Enter your choice (1-8): ").strip()

        if choice == "1":
            add_consumption()

        elif choice == "2":
            view_records()

        elif choice == "3":
            calculate_total()

        elif choice == "4":
            calculate_average()

        elif choice == "5":
            find_highest_lowest()

        elif choice == "6":
            forecast_consumption()

        elif choice == "7":
            save_records()

        elif choice == "8":
            save_records()
            print("Thank you for using the system!")
            break

        else:
            print("Invalid choice! Please select from 1 to 8.")


if __name__ == "__main__":
    main()

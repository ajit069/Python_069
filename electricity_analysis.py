
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

FILE_NAME = "electricity_data.csv"
FEATURES = ["lag_1", "lag_2", "lag_3", "rolling_mean_3", "month_number", "time_index"]
MODEL = None


def load_data():
    df_txt = pd.read_csv('electricity_data.txt', sep=',')
    if os.path.exists(FILE_NAME):
        try:
            df = pd.read_csv(FILE_NAME)
            if not {"Month", "Units"}.issubset(df.columns):
                raise ValueError("CSV must have Month and Units columns.")
            df["Month"] = pd.to_datetime(df["Month"], format="%Y-%m")
            df["Units"] = pd.to_numeric(df["Units"], errors="coerce")
            df = df.dropna(subset=["Month", "Units"])
            df = df.sort_values("Month").drop_duplicates("Month", keep="last")
            df["Month"] = df["Month"].dt.strftime("%Y-%m")
            print("Saved CSV data loaded.")
            return df.reset_index(drop=True)
        except (OSError, ValueError, KeyError) as error:
            print("Could not read CSV:", error)
            return pd.DataFrame(columns=["Month", "Units"])

    old_file = "electricity_data.txt"
    if os.path.exists(old_file):
        print("Importing old text-file records as year 2026.")
        records = []
        with open(old_file, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                try:
                    month_name, units = line.split(",")
                    month_number = pd.to_datetime(month_name, format="%B").month
                    records.append((f"2026-{month_number:02d}", float(units)))
                except ValueError:
                    print("Skipping invalid old record:", line)
        return pd.DataFrame(records, columns=["Month", "Units"]).sort_values("Month").reset_index(drop=True)

    print("No previous data found. Add monthly records first.")
    return pd.DataFrame(columns=["Month", "Units"])


def save_data(df):
    if df.empty:
        print("No records to save.")
        return
    output = df.copy()
    output["Month"] = pd.to_datetime(output["Month"]).dt.strftime("%Y-%m")
    output.sort_values("Month").to_csv(FILE_NAME, index=False)
    print("Records saved in", FILE_NAME)


def add_record(df):
    month = input("Enter month (YYYY-MM), e.g. 2026-01: ").strip()
    try:
        month = pd.to_datetime(month, format="%Y-%m").strftime("%Y-%m")
    except ValueError:
        print("Invalid format. Use YYYY-MM, such as 2026-01.")
        return df

    if month in df["Month"].astype(str).values:
        print("A record for this month already exists.")
        return df

    try:
        units = float(input("Enter electricity consumption in units: "))
        if units < 0:
            print("Consumption cannot be negative.")
            return df
    except ValueError:
        print("Please enter a valid number.")
        return df

    df = pd.concat([df, pd.DataFrame([[month, units]], columns=["Month", "Units"])], ignore_index=True)
    df["Month"] = pd.to_datetime(df["Month"]).dt.strftime("%Y-%m")
    return df.sort_values("Month").reset_index(drop=True)


def create_features(df):
    data = df.copy()
    data["Month"] = pd.to_datetime(data["Month"])
    data = data.sort_values("Month").reset_index(drop=True)
    data["lag_1"] = data["Units"].shift(1)
    data["lag_2"] = data["Units"].shift(2)
    data["lag_3"] = data["Units"].shift(3)
    data["rolling_mean_3"] = data["Units"].shift(1).rolling(3).mean()
    data["month_number"] = data["Month"].dt.month
    data["time_index"] = np.arange(len(data))
    return data.dropna().reset_index(drop=True)


def train_model(df):
    global MODEL
    if len(df) < 8:
        print("At least 8 monthly records are needed. Ideally, use 24 or more.")
        return

    featured = create_features(df)
    X = featured[FEATURES]
    y = featured["Units"]
    if len(featured) < 5:
        print("Not enough training examples after preparing features.")
        return

    # Chronological split: the latest records are kept for testing.
    test_count = max(1, int(round(len(featured) * 0.20)))
    if len(featured) - test_count < 3:
        test_count = 1

    X_train, X_test = X.iloc[:-test_count], X.iloc[-test_count:]
    y_train, y_test = y.iloc[:-test_count], y.iloc[-test_count:]

    test_model = RandomForestRegressor(
        n_estimators=300, max_depth=4, random_state=42
    )
    test_model.fit(X_train, y_train)
    predictions = test_model.predict(X_test)

    print("\n========== MODEL EVALUATION ==========")
    print("Algorithm: Random Forest Regressor")
    print("Training samples:", len(X_train))
    print("Testing samples:", len(X_test))
    print("MAE:", round(mean_absolute_error(y_test, predictions), 2), "units")
    print("RMSE:", round(np.sqrt(mean_squared_error(y_test, predictions)), 2), "units")
    if len(y_test) >= 2:
        print("R-squared:", round(r2_score(y_test, predictions), 3))
    else:
        print("R-squared: Not available with only one test sample.")

    comparison = pd.DataFrame({
        "Month": featured["Month"].iloc[-test_count:].dt.strftime("%Y-%m").values,
        "Actual": y_test.values,
        "Predicted": np.round(predictions, 2)
    })
    print("\nACTUAL VS PREDICTED")
    print(comparison.to_string(index=False))

    MODEL = RandomForestRegressor(n_estimators=300, max_depth=4, random_state=42)
    MODEL.fit(X, y)
    print("\nModel trained successfully on all available records.")
    print("Caution: a small dataset can produce unstable evaluation scores.")


def forecast_next_month(df):
    if MODEL is None:
        print("Please train the model first (menu option 5).")
        return
    if len(df) < 4:
        print("At least 4 monthly records are needed.")
        return

    history = df.copy()
    history["Month"] = pd.to_datetime(history["Month"])
    history = history.sort_values("Month").reset_index(drop=True)
    next_month = history["Month"].iloc[-1] + pd.DateOffset(months=1)
    values = history["Units"].astype(float).tolist()

    new_row = pd.DataFrame([{
        "lag_1": values[-1],
        "lag_2": values[-2],
        "lag_3": values[-3],
        "rolling_mean_3": float(np.mean(values[-3:])),
        "month_number": next_month.month,
        "time_index": len(values)
    }])
    prediction = max(0, float(MODEL.predict(new_row[FEATURES])[0]))

    print("\n========== NEXT MONTH FORECAST ==========")
    print("Forecast month:", next_month.strftime("%B %Y"))
    print("Predicted consumption:", round(prediction, 2), "units")
    print("Method: Random Forest Regression")
    print("This is an estimate, not a guaranteed value.")


def show_graph(df):
    if df.empty:
        print("No records available.")
        return
    dates = pd.to_datetime(df["Month"])
    plt.figure(figsize=(10, 5))
    plt.plot(dates, df["Units"], marker="o", label="Actual Consumption")
    plt.title("Monthly Electricity Consumption")
    plt.xlabel("Month")
    plt.ylabel("Consumption (units)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def main():
    df = load_data()
    while True:
        print("\n==========================================")
        print(" ELECTRICITY CONSUMPTION ANALYSIS SYSTEM")
        print("        MACHINE LEARNING VERSION")
        print("==========================================")
        print("1. Add Monthly Consumption")
        print("2. View Records")
        print("3. Calculate Total and Average")
        print("4. Find Highest and Lowest Consumption")
        print("5. Train and Evaluate ML Model")
        print("6. Forecast Next Month")
        print("7. Display Consumption Graph")
        print("8. Save Records")
        print("9. Exit")
        choice = input("Enter your choice (1-9): ").strip()

        if choice == "1":
            df = add_record(df)
        elif choice == "2":
            if df.empty:
                print("No records available.")
            else:
                print(df.to_string(index=False))
        elif choice == "3":
            if df.empty:
                print("No records available.")
            else:
                print("Total:", round(df["Units"].sum(), 2), "units")
                print("Average:", round(df["Units"].mean(), 2), "units")
        elif choice == "4":
            if df.empty:
                print("No records available.")
            else:
                high = df.loc[df["Units"].idxmax()]
                low = df.loc[df["Units"].idxmin()]
                print("Highest:", high["Month"], "-", high["Units"], "units")
                print("Lowest:", low["Month"], "-", low["Units"], "units")
        elif choice == "5":
            train_model(df)
        elif choice == "6":
            forecast_next_month(df)
        elif choice == "7":
            show_graph(df)
        elif choice == "8":
            save_data(df)
        elif choice == "9":
            save_data(df)
            print("Thank you for using the system!")
            break
        else:
            print("Invalid choice. Select from 1 to 9.")


if __name__ == "__main__":
    main()


from pathlib import Path
import pandas as pd
import numpy as np

# Main dataset folder
input_folder = Path("NAB-master/data")

# Reports folder
report_folder = Path("report")
report_folder.mkdir(exist_ok=True)

# Find all CSV files
files = [
    file for file in input_folder.rglob("*.csv")
    if "cleaned data" not in file.parts
    and "report" not in file.parts
]

print("Total CSV files found:", len(files))

# Empty list to store loaded datasets
all_data = []

# Load CSV files one by one
for file in files:

    try:
        df = pd.read_csv(file)

        all_data.append({
            "file_name": file.name,
            "data": df
        })

        print("Loaded:", file.name, df.shape)

    except Exception as e:
        print("Error:", file.name, e)

print("\nTotal files loaded:", len(all_data))





column_name_report = []

print("\nStarting Column Name Validation...\n")

for item in all_data:

    file_name = item["file_name"]
    df = item["data"]

    # Get column names
    columns = list(df.columns)

    # Check missing column names
    missing_names = sum(
        str(col).strip() == "" or str(col).lower().startswith("unnamed:")
        for col in columns
    )

    # Check duplicate column names
    duplicate_names = sum(
        df.columns.duplicated()
    )

    # Check extra spaces
    extra_spaces = sum(
        str(col) != str(col).strip()
        for col in columns
    )

    # Check expected columns
    expected_columns = {"timestamp", "value"}

    actual_columns = {
        str(col).strip().lower()
        for col in columns
    }

    missing_expected = expected_columns - actual_columns

    # Save results
    column_name_report.append({
        "File_Name": file_name,
        "Total_Columns": len(columns),
        "Column_Names": ", ".join(map(str, columns)),
        "Missing_Names": missing_names,
        "Duplicate_Names": duplicate_names,
        "Extra_Spaces": extra_spaces,
        "Missing_Expected_Columns": ", ".join(sorted(missing_expected))
    })

    print("Checked:", file_name)

# Save column name report
pd.DataFrame(column_name_report).to_csv(
    report_folder / "column_name_report.csv",
    index=False
)

print("\nColumn Name Validation Completed!")
print("Report saved in Reports folder.")





missing_value_report = []

print("\nStarting Missing Values Validation...\n")

for item in all_data:

    file_name = item["file_name"]
    df = item["data"]

    # Total rows
    total_rows = len(df)

    # Check missing values in each column
    missing_timestamp = df["timestamp"].isnull().sum()
    missing_value = df["value"].isnull().sum()

    # Total missing values
    total_missing = df.isnull().sum().sum()

    # Save results
    missing_value_report.append({
        "File_Name": file_name,
        "Total_Rows": total_rows,
        "Missing_Timestamp": missing_timestamp,
        "Missing_Value": missing_value,
        "Total_Missing_Values": total_missing
    })

    print("Checked:", file_name)

# Save missing values report
pd.DataFrame(missing_value_report).to_csv(
    report_folder / "missing_value_report.csv",
    index=False
)

print("\nMissing Values Validation Completed!")
print("Report saved in report folder.")



duplicate_report = []

print("\nStarting Duplicate Rows Validation...\n")

for item in all_data:

    file_name = item["file_name"]
    df = item["data"]

    # Count total rows
    total_rows = len(df)

    # Check duplicate rows
    duplicate_rows = df.duplicated().sum()

    # Calculate unique rows
    unique_rows = total_rows - duplicate_rows

    # Save results
    duplicate_report.append({
        "File_Name": file_name,
        "Total_Rows": total_rows,
        "Duplicate_Rows": duplicate_rows,
        "Unique_Rows": unique_rows
    })

    print("Checked:", file_name)

# Save duplicate rows report
pd.DataFrame(duplicate_report).to_csv(
    report_folder / "duplicate_rows_report.csv",
    index=False
)

print("\nDuplicate Rows Validation Completed!")
print("Report saved in report folder.")




datatype_report = []

print("\nStarting Data Type Validation...\n")

for item in all_data:

    file_name = item["file_name"]
    df = item["data"]

    # Check data type of each column
    for column in df.columns:

        data_type = str(df[column].dtype)

        # Save results
        datatype_report.append({
            "File_Name": file_name,
            "Column_Name": column,
            "Data_Type": data_type
        })

    print("Checked:", file_name)

# Save data type report
pd.DataFrame(datatype_report).to_csv(
    report_folder / "datatype_report.csv",
    index=False
)

print("\nData Type Validation Completed!")
print("Report saved in report folder.")












# PART 6: DATA CLEANING

cleaned_folder = Path("cleaned data")
cleaned_folder.mkdir(exist_ok=True)

cleaning_report = []

print("\nStarting Data Cleaning...\n")

for item in all_data:

    file_name = item["file_name"]

    # Create a copy of original data
    df = item["data"].copy()

    original_rows = len(df)

    # Step 1: Remove missing required values
    missing_rows = df[["timestamp", "value"]].isnull().any(axis=1).sum()

    df = df.dropna(subset=["timestamp", "value"])

    # Step 2: Convert timestamp into datetime
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    # Count invalid timestamps
    invalid_timestamps = df["timestamp"].isnull().sum()

    # Remove invalid timestamps
    df = df.dropna(subset=["timestamp"])

    # Step 3: Convert value into numeric
    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce"
    )

    # Count invalid values
    invalid_values = df["value"].isnull().sum()

    # Remove invalid values
    df = df.dropna(subset=["value"])

    # Step 4: Remove duplicate rows
    duplicate_rows = df.duplicated().sum()

    df = df.drop_duplicates()

    # Step 5: Save cleaned CSV file
    df.to_csv(
        cleaned_folder / file_name,
        index=False
    )

    # Step 6: Save cleaning report
    cleaning_report.append({
        "File_Name": file_name,
        "Original_Rows": original_rows,
        "Missing_Rows_Removed": missing_rows,
        "Invalid_Timestamps": invalid_timestamps,
        "Invalid_Values": invalid_values,
        "Duplicate_Rows_Removed": duplicate_rows,
        "Final_Rows": len(df)
    })

    print("Cleaned:", file_name)

# Save cleaning report
pd.DataFrame(cleaning_report).to_csv(
    report_folder / "data_cleaning_report.csv",
    index=False
)

print("\nData Cleaning Completed!")
print("Cleaned files saved in cleaned data folder.")
print("Cleaning report saved in report folder.")

# Get all cleaned CSV files
cleaned_files = list(cleaned_folder.glob("*.csv"))

print("Total Cleaned Files:", len(cleaned_files))




# PART 7: CLEANED DATA VALIDATION

validation_report = []

for file in cleaned_files:

    df = pd.read_csv(file)

    # Step 1: Check missing values
    missing_values = df.isnull().sum().sum()

    # Step 2: Validate timestamp
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    invalid_timestamps = df["timestamp"].isnull().sum()

    # Step 3: Validate numeric values
    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce"
    )

    invalid_values = df["value"].isnull().sum()

    # Step 4: Check duplicate rows
    duplicate_rows = df.duplicated().sum()

    # Step 5: Store results
    validation_report.append({
        "File_Name": file.name,
        "Total_Rows": len(df),
        "Missing_Values": missing_values,
        "Invalid_Timestamps": invalid_timestamps,
        "Invalid_Values": invalid_values,
        "Duplicate_Rows": duplicate_rows,
        "Timestamp_Dtype": str(df["timestamp"].dtype),
        "Value_Dtype": str(df["value"].dtype)
    })

    print("Validated:", file.name)


# Save validation report
pd.DataFrame(validation_report).to_csv(
    report_folder / "cleaned_data_validation_report.csv",
    index=False
)

print("\nCleaned Data Validation Completed!")
print("Total Cleaned Files:", len(cleaned_files))



# PART 8: COMBINE CLEANED DATASETS

combined_folder = Path("combined data")
combined_folder.mkdir(exist_ok=True)

combined_data = []

for file in cleaned_files:

    df = pd.read_csv(file)

    # Original file ka naam save karna
    df["Source_File"] = file.name

    combined_data.append(df)

if combined_data:

    combined_df = pd.concat(combined_data, ignore_index=True)

    # Combined CSV save karna
    combined_df.to_csv(
        combined_folder / "combined_dataset.csv",
        index=False
    )

    print("\nCombined Dataset Created Successfully!")
    print("Total Files:", len(cleaned_files))
    print("Total Rows:", len(combined_df))
    print("Total Columns:", len(combined_df.columns))
    print("Saved in: combined data/combined_dataset.csv")

else:
    print("No cleaned CSV files found!")
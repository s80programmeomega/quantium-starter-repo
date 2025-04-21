import os
from pathlib import Path

import magic
import pandas as pd


RESULT_FILE_PATH = "./output/converted/result.csv"
CONVERTED_FILE_PATH = "./output/converted/converted.csv"


def extract_data(input_dir: Path, output_dir: Path):
    output = Path(output_dir)/"converted"
    os.makedirs(output, exist_ok=True)
    csv_count = 0

    with os.scandir(input_dir) as entries:
        if not entries:
            print("No files found in the input directory.")
        open(RESULT_FILE_PATH, "w").close()

        open(output/"result.csv", "w").close()
        for entry in entries:
            if entry.is_file():
                csv_count = process_file(entry.path, csv_count)

        print(f"Total CSV files processed: {csv_count}")
    return output


def process_file(entry, count=0):
    magic_type = magic.from_file(entry, mime=True)
    if magic_type == "text/csv":
        process_csv(entry)
        count += 1
    else:
        print(f"Skipping file ==> {entry}, \nas it is not a CSV file.")
    return count


def process_csv(entry):

    df_chunks = pd.read_csv(entry, header='infer',
                            chunksize=100, low_memory=True)
    result_file = "./output/converted/result.csv"

    # Check if the output file does not exist, or if the file is empty
    write_header = not os.path.exists(
        result_file) or os.path.getsize(result_file) == 0

    with open(result_file, "a") as f:
        for i, df in enumerate(df_chunks):
            # Check if all required columns exist
            required_columns = {'product', 'price',
                                'quantity', 'date', 'region'}
            if required_columns.issubset(df.columns):
                f.write(df[df["product"] == "pink morsel"].to_csv(
                    index=False, header=write_header))

                # After writing the header once, set the flag to False
                write_header = False
            else:
                continue

    print(f"Processed CSV file: {entry}")
    return result_file


def convert_data():
    print("Converting data...")

    # Check if the output file does not exist, or if the file is empty
    open(CONVERTED_FILE_PATH, "w").close()
    write_hader = not os.path.exists(
        CONVERTED_FILE_PATH) or os.path.getsize(
        CONVERTED_FILE_PATH) == 0
    with open(RESULT_FILE_PATH, "r") as f:
        chunks = pd.read_csv(f, chunksize=100, index_col=None)
        with open(CONVERTED_FILE_PATH, "a") as f_out:
            for i, df in enumerate(chunks):
                df["price"] = df["price"].str.replace(
                    "[$,]", "", regex=True).astype(float)
                df["sales"] = df["price"] * df["quantity"]
                df["date"] = pd.to_datetime(df["date"])
                df.drop(columns=["product", "quantity", "price"], inplace=True)

                # reorganise the columns
                df = df[["sales", "date", "region"]]
                df.columns = df.columns.str.capitalize()

                # wrtite to the file
                df.to_csv(f_out, index=False, header=write_hader)
                write_hader = False

    print("Data conversion completed.")
    print(f"Converted data saved to {CONVERTED_FILE_PATH}")


if __name__ == "__main__":
    input_dir = Path("./data")
    output_dir = Path("./output")
    extract_data(input_dir, output_dir)
    convert_data()

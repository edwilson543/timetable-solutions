"""Quick script for converting a fixture saved as json to a csv, which can then be used to test csv upload."""

# Standard library imports
import json
from pathlib import Path

# Third party imports
import pandas as pd


# io settings
loc = Path(__file__).parent / "timetable" / "view_timetables" / "fixtures"
output_loc = Path(__file__).parent / "timetable" / "data_upload" / "test_data"
files = ["classes"]

if __name__ == "__main__":
    for filename in files:
        filepath = loc / (filename + ".json")
        with open(filepath, "r") as read_f:
            data = json.load(read_f)
            fields = []
            df_data = {}
            for n, item in enumerate(data):
                field_data = item["fields"]
                if n == 0:
                    df_data["pk"] = [item["pk"]]
                    for key, value in field_data.items():
                        df_data[key] = [value]
                else:
                    df_data["pk"].append(item["pk"])
                    for key, value in field_data.items():
                        df_data[key].append(value)
        df = pd.DataFrame(df_data)
        output_filepath = output_loc / (filename + ".csv")
        df.to_csv(output_filepath, index=False)

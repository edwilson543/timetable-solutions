"""Quick script for updating fixtures ad hoc, when not possible by a migration"""

# Standard library imports
import json
from pathlib import Path
from typing import List


# io settings
loc = Path(__file__).parents[1] / "timetable" / "timetable_selector" / "fixtures"
input_filename = "classes.json"
output_filename = "new_classes.json"
school_access_key = 1
# old_id_column = "pupil_id"
print(output_filename)


if __name__ == "__main__":
    with open(loc / input_filename, "r") as file:
        json_data = file.read()
        pyt_data: List = json.loads(json_data)
        new_pyt_data = []
        for n, item in enumerate(pyt_data):
            new_item = item.copy()
            new_item["pk"] = n + 1
            new_item["fields"]["class_id"] = item["pk"]
            new_item["fields"]["school_id"] = school_access_key
            # new_item["pk"] = item["pk"]
            new_pyt_data.append(new_item)

    with open(loc / output_filename, "w") as write_file:
        json.dump(new_pyt_data, write_file)
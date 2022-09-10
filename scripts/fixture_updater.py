"""Quick script for updating fixtures ad hoc, when not possible by a migration"""

# Standard library imports
import json
from pathlib import Path
from typing import List


# io settings
loc = Path(__file__).parents[1] / "timetable" / "data" / "fixtures"
input_filenames = ["timetable.json"]
output_filenames = ["timetable.json"]
# new_model_name = "data.fixedclass"


def update_fixture(input_fixture_file: str, output_fixture_file: str, location: Path = loc) -> None:
    with open(location / input_fixture_file, "r") as file:
        json_data = file.read()
        pyt_data: List = json.loads(json_data)
        new_pyt_data = []
        for n, item in enumerate(pyt_data):
            new_item = item.copy()
            new_item["fields"]["period_starts_at"] = new_item["fields"]["period_start_time"]
            new_item["fields"].pop("period_start_time")
            new_pyt_data.append(new_item)

    with open(location / output_fixture_file, "w") as write_file:
        json.dump(new_pyt_data, write_file)


if __name__ == "__main__":
    for n, fixture in enumerate(input_filenames):
        update_fixture(input_fixture_file=fixture, output_fixture_file=output_filenames[n])

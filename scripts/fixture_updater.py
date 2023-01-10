"""Quick script for updating fixtures ad hoc, when not possible by a migration"""

# Standard library imports
import json
from pathlib import Path

# io settings
loc = (
    Path(__file__).parents[1]
    / "timetable_solutions"
    / "tests"
    / "test_scenario_fixtures"
)
input_filenames = [
    "test_scenario_1.json",
    "test_scenario_2.json",
    "test_scenario_3.json",
    "test_scenario_4.json",
    "test_scenario_5.json",
    "test_scenario_6.json",
    "test_scenario_7.json",
    "test_scenario_8.json",
    "test_scenario_9.json",
    "test_scenario_10.json",
    "test_scenario_objective_1.json",
    "test_scenario_objective_2.json",
]
output_filenames = input_filenames


def update_fixture(
    input_fixture_file: str,
    output_fixture_file: str,
    location: Path = loc,
    fixture_no: int | None = None,
) -> None:
    with open(location / input_fixture_file, "r") as file:
        json_data = file.read()
        pyt_data: list = json.loads(json_data)
        new_pyt_data = []
        for n, item in enumerate(pyt_data):
            new_item = item.copy()

            if new_item["model"] == "data.timetableslot":
                new_item["fields"]["relevant_year_groups"] = [(fixture_no) * 100 + 1]

            new_pyt_data.append(new_item)

    with open(location / output_fixture_file, "w") as write_file:
        json.dump(new_pyt_data, write_file)


if __name__ == "__main__":
    for n, fixture in enumerate(input_filenames):
        update_fixture(
            input_fixture_file=fixture,
            output_fixture_file=output_filenames[n],
            fixture_no=(n + 1),
        )

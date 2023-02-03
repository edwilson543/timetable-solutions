# Standard library imports
import io

# Third party imports
from pandas import errors as pandas_errors


def get_csv_from_lists(list_data: list[list[str | int | float | None]]) -> io.BytesIO:
    """Create a file-like object from a list of lists."""
    # Perform some checks that don't raise for a simulated upload
    # But would for a real one
    n_headers = len(list_data[0])
    max_columns = max(len(sublist) for sublist in list_data)
    if max_columns > n_headers:
        raise pandas_errors.ParserError(
            "CSV data contains additional columns not defined in the headers."
        )

    csv_file_str = "".join(_list_to_csv_row(sublist) for sublist in list_data)
    csv_file_bytes = csv_file_str.encode("utf-8")

    stream = io.BytesIO()
    stream.write(csv_file_bytes)
    stream.seek(0)

    return stream


def _list_to_csv_row(csv_row: list[str | int | float | None]) -> str:
    """Convert a python list to a row in a csv file, represented as a string."""

    def __clean_item(item: str | int | float | None) -> str | int | float:
        """Wrap strings with commas in quotes, and filter None."""
        if isinstance(item, str) and "," in item:
            item = '"' + item + '"'
        if item is None:
            item = ""
        return item

    row = "".join([f"{__clean_item(item)}," for item in csv_row])
    # Remove last comma and add a newline characters
    return row[:-1] + "\n"

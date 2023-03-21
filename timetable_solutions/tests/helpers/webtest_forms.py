# Third party imports
import webtest


def select_multiple(form: webtest.Form, *, field_name: str, selection: list) -> None:
    """
    Fill out a multiselect widget.

    The html used for multiseleect uses multiple <input> tags with the same name,
    so when trying to do form["multiselect-field"], webtest raises an error.
    This helper function gets round that issue.
    """
    field = form.fields[field_name]
    for option in field:
        option.checked = option._value in selection

"""
Module containing the TimetableFileUploadProccessor only.
"""

# Third party imports
import pandas as pd

# Local application imports
from data import models
from domain.data_management.constants import Header, UploadFileStructure
from domain.data_management.timetable_slot import operations
from domain.data_management.upload_processors._base import (
    BaseFileUploadProcessor,
    RelationalUploadProcessorMixin,
)


class TimetableSlotFileUploadProcessor(
    BaseFileUploadProcessor, RelationalUploadProcessorMixin
):
    """
    Processor of csv files containing teacher data
    """

    model = models.TimetableSlot
    file_structure = UploadFileStructure.TIMETABLE
    creation_callback = operations.create_new_timetable_slot

    def _get_data_dict_from_row_for_create_new(  # type: ignore  # mypy flags changed return type versus base class
        self, row: pd.Series, row_number: int
    ) -> dict | None:
        """
        Customisation of the base class' method for extracting data from the row.
        The output is a dictionary which can be passed directly to the Lesson model's create_new method.
        """
        create_new_dict = super()._get_data_dict_from_row_for_create_new(
            row=row, row_number=row_number
        )
        if create_new_dict is None:
            if self.upload_error_message is None:
                self.upload_error_message = (
                    f"Could not process data in row: {row_number}, please amend!"
                )

        if Header.RELEVANT_YEAR_GROUP_IDS in create_new_dict.keys():
            raw_year_group_string = create_new_dict.pop(Header.RELEVANT_YEAR_GROUP_IDS)
            year_groups = super()._get_year_groups_from_raw_year_group_string(
                raw_year_group_string=raw_year_group_string, row_number=row_number
            )
            if year_groups:
                create_new_dict[
                    models.TimetableSlot.Constant.relevant_year_groups
                ] = year_groups
                return create_new_dict
            else:
                self.upload_error_message = (
                    f"Invalid year groups: {raw_year_group_string} in row: {row_number}. "
                    f"Please amend!"
                )
                return None
        else:
            self.upload_error_message = (
                f"No year groups were referenced in row {row_number}!"
            )
            return None

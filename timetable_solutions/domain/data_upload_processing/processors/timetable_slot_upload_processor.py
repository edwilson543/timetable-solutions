"""
Module containing the TimetableFileUploadProccessor only.
"""

import pandas as pd

from data import models
from domain.data_upload_processing.constants import UploadFileStructure, Header
from domain.data_upload_processing.processors.base_processors import (
    BaseFileUploadProcessor,
    M2MUploadProcessorMixin,
)


class TimetableSlotFileUploadProcessor(
    BaseFileUploadProcessor, M2MUploadProcessorMixin
):
    """
    Processor of csv files containing teacher data
    """

    model = models.TimetableSlot
    file_structure = UploadFileStructure.TIMETABLE

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

        if Header.RELEVANT_YEAR_GROUPS in create_new_dict.keys():
            raw_year_group_string = create_new_dict.pop(Header.RELEVANT_YEAR_GROUPS)
            year_groups = self._get_year_groups_from_raw_year_group_string(
                raw_year_group_string=raw_year_group_string, row_number=row_number
            )
            if year_groups:
                create_new_dict[Header.RELEVANT_YEAR_GROUPS] = year_groups
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

    def _get_year_groups_from_raw_year_group_string(
        self,
        raw_year_group_string: str,
        row_number: int,
    ) -> models.YearGroupQuerySet | None:
        """
        Method providing a reduced entry point to M2MUploadProcessorMixin's get_id_set_from_string method,
        by only offering 2 of the arguments (which is what we always want for this processor.

        :return A set of ids, representing pupil ids or timetable slot ids.
        """

        year_group_string_set = super().get_id_set_from_string(
            raw_string_of_ids=raw_year_group_string,
            row_number=row_number,
            target_id_type=str,
        )
        if year_group_string_set is None or len(year_group_string_set) == 0:
            self.upload_error_message = (
                f"Invalid year groups: {raw_year_group_string} in row: {row_number}. "
                f"Please amend!"
            )
            return None

        year_groups = models.YearGroup.objects.get_specific_year_groups(
            school_id=self._school_access_key, year_groups=year_group_string_set
        )

        if year_groups.count() < len(year_group_string_set):
            missing_year_groups = year_group_string_set - {
                yg.year_group for yg in year_groups
            }
            self.upload_error_message = (
                f"No year_group(s) with ids: {missing_year_groups} were found, "
                f"referenced in row {row_number}!"
            )
            return None

        return year_groups

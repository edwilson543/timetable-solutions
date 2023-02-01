# Standard library imports
import re

# Third party imports
import pandas as pd

# Django imports
from django.core.files.uploadedfile import UploadedFile

# Local application imports
from domain.data_upload_processing.constants import Header, UploadFileStructure
from domain.data_upload_processing.processors._base import (
    BaseFileUploadProcessor,
    M2MUploadProcessorMixin,
)
from data import models


class BreakFileUploadProcessor(BaseFileUploadProcessor, M2MUploadProcessorMixin):
    """Processing class for a user file upload defining 'Break' data."""

    model = models.Break
    file_structure = UploadFileStructure.BREAK

    def __init__(
        self,
        school_access_key: int,
        csv_file: UploadedFile,
        attempt_upload: bool = True,
    ):
        super().__init__(
            school_access_key=school_access_key,
            csv_file=csv_file,
            attempt_upload=attempt_upload,
        )

    def _get_data_dict_from_row_for_create_new(
        self, row: pd.Series, row_number: int
    ) -> dict:
        """
        Customisation of the base class' method for extracting data from the row.
        The output is a dictionary which can be passed directly to the Lesson model's create_new method.
        """
        create_new_dict = super()._get_data_dict_from_row_for_create_new(
            row=row, row_number=row_number
        )

        if Header.TEACHER_IDS in create_new_dict:
            raw_teacher_ids = create_new_dict.pop(Header.TEACHER_IDS)
            teachers = self._get_teachers_from_raw_teacher_ids_string(
                teacher_ids_raw=raw_teacher_ids,
                row_number=row_number,
            )
            if teachers and not self.upload_error_message:
                create_new_dict[models.Break.Constant.teachers] = teachers

        if Header.RELEVANT_YEAR_GROUPS in create_new_dict:
            raw_year_group_string = create_new_dict.pop(Header.RELEVANT_YEAR_GROUPS)
            year_groups = super()._get_year_groups_from_raw_year_group_string(
                raw_year_group_string=raw_year_group_string, row_number=row_number
            )
            if year_groups and not self.upload_error_message:
                create_new_dict[
                    models.Break.Constant.relevant_year_groups
                ] = year_groups

        create_new_dict_ = {
            key: value for key, value in create_new_dict.items() if value is not None
        }
        return create_new_dict_

    def _get_teachers_from_raw_teacher_ids_string(
        self, teacher_ids_raw: str, row_number: int
    ) -> models.TeacherQuerySet | None:
        """Method to retrieve a queryset of Teachers from a raw user-upload string."""
        teacher_ids = super().get_integer_set_from_string(
            raw_string_of_ids=teacher_ids_raw, row_number=row_number
        )
        if teacher_ids is not None:
            teachers = models.Teacher.objects.get_specific_teachers(
                school_id=self._school_access_key, teacher_ids=teacher_ids
            )
            if teachers.count() < len(teacher_ids):
                missing_slots = set(teacher_ids) - {
                    teacher.teacher_id for teacher in teachers
                }
                self.upload_error_message = (
                    f"No teacher(s) with ids: {missing_slots} were found!"
                )
                return None

            else:
                return teachers

        self.upload_error_message = (
            f"Could not interpret {teacher_ids_raw} for lesson in row {row_number}. "
            "All lessons must have some pupils."
        )
        return None

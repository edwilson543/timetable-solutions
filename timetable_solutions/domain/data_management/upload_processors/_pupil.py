# Third party imports
import pandas as pd

# Local application imports
from data import models
from domain.data_management.constants import Header, UploadFileStructure
from domain.data_management.upload_processors._base import (
    BaseFileUploadProcessor,
    RelationalUploadProcessorMixin,
)


class PupilFileUploadProcessor(BaseFileUploadProcessor, RelationalUploadProcessorMixin):
    """
    Processor of csv files containing pupil data.
    The pupil file contains one relational column, the year_group_id.
    """

    model = models.Pupil
    file_structure = UploadFileStructure.PUPILS

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

        if Header.YEAR_GROUP_ID in create_new_dict:
            raw_yg_id = create_new_dict.pop(Header.YEAR_GROUP_ID)
            create_new_dict[
                Header.YEAR_GROUP_ID
            ] = super().get_clean_id_from_file_field_value(
                user_input_id=raw_yg_id,
                row_number=row_number,
                field_name="year_group_ids",
            )
        else:
            self.upload_error_message = f"Invalid year group specified in row {row_number}. All pupils must have a year group!"
        return create_new_dict

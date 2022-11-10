"""
All views relating to the data upload page
"""
from .data_upload_page import UploadPage
from .upload_views import (PupilListUpload, TeacherListUpload, ClassroomListUpload, TimetableStructureUpload,
                           UnsolvedClassUpload, FixedClassUpload)
from .reset_views import (PupilListReset, TeacherListReset, ClassroomListReset, TimetableStructureReset,
                          UnsolvedClassReset, FixedClassReset, AllSchoolDataReset)

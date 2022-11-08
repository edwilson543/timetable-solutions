"""Module containing integration tests for the FileUploadProcessor"""

# Standard library imports
import datetime as dt

# Django imports
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

# Local application imports
from data import models
from domain import data_upload_processing
from tests.input_settings import TEST_DATA_DIR


# TODO - error cases to test
# file contains error in bottom row -> nothing saved
# file contains not unique unique togethers -> nothing saved
    # First do all the unique togethers, and test
# blank values instead of empty lists are handled in the right way
    # this could be captured within the current tests (mix and match)

class TestFileUploadProcessorIndependentFiles(TestCase):
    """Tests for the file uploads that depend on no existing data in the database"""

    fixtures = ["user_school_profile.json"]
    valid_uploads = TEST_DATA_DIR / "valid_uploads"

    def test_upload_teachers_to_database_valid_upload(self):
        """Test that the FileUploadProcessor can upload the teacher csv file and use it to populate database"""
        # Upload the file
        with open(self.valid_uploads / "teachers.csv", "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())
            upload_processor = data_upload_processing.FileUploadProcessor(
                csv_file=upload_file, csv_headers=data_upload_processing.UploadFileStructure.TEACHERS.headers,
                id_column_name=data_upload_processing.UploadFileStructure.TEACHERS.id_column,
                model=models.Teacher, school_access_key=123456)

        # Test the upload was successful
        self.assertTrue(upload_processor.upload_successful)
        self.assertEqual(upload_processor.n_model_instances_created, 11)

        # Test the database is as expected
        all_teachers = models.Teacher.objects.get_all_instances_for_school(school_id=123456)
        self.assertEqual(len(all_teachers), 11)
        greg = models.Teacher.objects.get_individual_teacher(school_id=123456, teacher_id=6)
        self.assertIsInstance(greg, models.Teacher)
        self.assertEqual(greg.firstname, "Greg")
        self.assertEqual(greg.surname, "Thebaker")

    def test_upload_pupils_to_database_valid_upload(self):
        """Test that the FileUploadProcessor can upload the pupil csv file and use it to populate database"""
        # Upload the file
        with open(self.valid_uploads / "pupils.csv", "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())
            upload_processor = data_upload_processing.FileUploadProcessor(
                csv_file=upload_file, csv_headers=data_upload_processing.UploadFileStructure.PUPILS.headers,
                id_column_name=data_upload_processing.UploadFileStructure.PUPILS.id_column,
                model=models.Pupil, school_access_key=123456)

        # Test the upload was successful
        self.assertTrue(upload_processor.upload_successful)
        self.assertEqual(upload_processor.n_model_instances_created, 6)

        # Test that the database is as expected
        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        self.assertEqual(len(all_pupils), 6)
        teemu = models.Pupil.objects.get_individual_pupil(school_id=123456, pupil_id=5)
        self.assertEqual(teemu.firstname, "Teemu")
        self.assertEqual(teemu.surname, "Pukki")

    def test_upload_classrooms_to_database_valid_upload(self):
        """Test that the FileUploadProcessor can upload the classroom csv file and use it to populate database"""
        # Upload the file
        with open(self.valid_uploads / "classrooms.csv", "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())
            upload_processor = data_upload_processing.FileUploadProcessor(
                csv_file=upload_file, csv_headers=data_upload_processing.UploadFileStructure.CLASSROOMS.headers,
                id_column_name=data_upload_processing.UploadFileStructure.CLASSROOMS.id_column,
                model=models.Classroom, school_access_key=123456)

        # Test the upload was successful
        self.assertTrue(upload_processor.upload_successful)
        self.assertEqual(upload_processor.n_model_instances_created, 12)

        # Test that the database is as expected
        all_classrooms = models.Classroom.objects.get_all_instances_for_school(school_id=123456)
        self.assertEqual(len(all_classrooms), 12)
        room = models.Classroom.objects.get_individual_classroom(school_id=123456, classroom_id=11)
        self.assertEqual(room.room_number, 40)

    def test_upload_timetable_structure_to_database_valid_upload(self):
        """Test that the FileUploadProcessor can upload the timetable csv file and use it to populate database"""
        # Upload the file
        with open(self.valid_uploads / "timetable.csv", "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())
            upload_processor = data_upload_processing.FileUploadProcessor(
                csv_file=upload_file, csv_headers=data_upload_processing.UploadFileStructure.TIMETABLE.headers,
                id_column_name=data_upload_processing.UploadFileStructure.TIMETABLE.id_column,
                model=models.TimetableSlot, school_access_key=123456)

        # Test the upload was successful
        self.assertTrue(upload_processor.upload_successful)
        self.assertEqual(upload_processor.n_model_instances_created, 35)

        # Test that the database is as expected
        all_slots = models.TimetableSlot.objects.get_all_instances_for_school(school_id=123456)
        self.assertEqual(len(all_slots), 35)
        slot = models.TimetableSlot.objects.get_individual_timeslot(school_id=123456, slot_id=1)
        self.assertEqual(slot.day_of_week, 1)
        self.assertEqual(slot.period_starts_at, dt.time(hour=9))
        self.assertEqual(slot.period_duration, dt.timedelta(hours=1))


class TestFileUploadProcessorDependentFiles(TestCase):
    """Tests for the file uploads that depend on no existing data in the database, hence requiring fixtures."""

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json"]
    valid_uploads = TEST_DATA_DIR / "valid_uploads"

    def test_upload_unsolved_classes_to_database_valid_upload(self):
        """
        Test that the FileUploadProcessor can upload the class requirements (unsolved classes) csv file and use it
        to populate database
        """
        # Upload the file
        with open(self.valid_uploads / "class_requirements.csv", "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())
            upload_processor = data_upload_processing.FileUploadProcessor(
                csv_file=upload_file, csv_headers=data_upload_processing.UploadFileStructure.UNSOLVED_CLASSES.headers,
                id_column_name=data_upload_processing.UploadFileStructure.UNSOLVED_CLASSES.id_column,
                model=models.UnsolvedClass, school_access_key=123456, is_unsolved_class_upload=True)

        # Test the upload was successful
        self.assertTrue(upload_processor.upload_successful)
        self.assertEqual(upload_processor.n_model_instances_created, 12)

        # Test the database is as expected
        all_classes = models.UnsolvedClass.objects.get_all_instances_for_school(school_id=123456)
        self.assertEqual(len(all_classes), 12)
        classes_with_teachers = sum([1 for klass in all_classes if klass.teacher is not None])
        self.assertEqual(classes_with_teachers, 12)
        total_non_unique_pupils = sum([klass.pupils.count() for klass in all_classes])
        self.assertEqual(total_non_unique_pupils, 18)

        # Spot check on one specific UnsolvedClass
        klass = models.UnsolvedClass.objects.get_individual_unsolved_class(school_id=123456,
                                                                           class_id="YEAR_ONE_MATHS_A")
        self.assertQuerysetEqual(klass.pupils.all(), models.Pupil.objects.filter(pupil_id__in={1, 2}), ordered=False)
        self.assertEqual(klass.teacher, models.Teacher.objects.get_individual_teacher(school_id=123456, teacher_id=1))

    def test_upload_fixed_classes_to_database_valid_upload(self):
        """
        Test that the FileUploadProcessor can upload the fixed classes csv file and use it to populate database
        """
        # Upload the file
        with open(self.valid_uploads / "fixed_classes.csv", "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())
            upload_processor = data_upload_processing.FileUploadProcessor(
                csv_file=upload_file, csv_headers=data_upload_processing.UploadFileStructure.FIXED_CLASSES.headers,
                id_column_name=data_upload_processing.UploadFileStructure.FIXED_CLASSES.id_column,
                model=models.FixedClass, school_access_key=123456, is_fixed_class_upload=True)

        # Test the upload was successful
        self.assertTrue(upload_processor.upload_successful)
        self.assertEqual(upload_processor.n_model_instances_created, 12)

        # Test the database is as expected
        all_classes = models.FixedClass.objects.get_all_instances_for_school(school_id=123456)
        self.assertEqual(len(all_classes), 12)
        classes_with_teachers = sum([1 for klass in all_classes if klass.teacher is not None])
        self.assertEqual(classes_with_teachers, 11)
        total_non_unique_pupils = sum([klass.pupils.count() for klass in all_classes])
        self.assertEqual(total_non_unique_pupils, 6)
        total_non_unique_slots = sum([klass.time_slots.count() for klass in all_classes])
        self.assertEqual(total_non_unique_slots, 60)

        # Spot checks on a couple of specific FixedClasses
        pup_lunch = models.FixedClass.objects.get_individual_fixed_class(school_id=123456, class_id="LUNCH_PUPILS")
        self.assertQuerysetEqual(pup_lunch.pupils.all(),
                                 models.Pupil.objects.get_all_instances_for_school(school_id=123456), ordered=False)

        teach_ten_lunch = models.FixedClass.objects.get_individual_fixed_class(school_id=123456, class_id="LUNCH_10")
        self.assertEqual(teach_ten_lunch.teacher,
                         models.Teacher.objects.get_individual_teacher(school_id=123456, teacher_id=10))

"""
Convenience imports of all ModelSerializer subclasses
The solver only needs to be aware of FixedClass, UnsolvedClass, and TimetableSlot - all other models e.g. pupils are
identifiable from the model field relationships, and suffice to be represented by primary keys only within the solver.
"""
from .fixed_class_serialiser import FixedClass
from .unsolved_class_serialiser import UnsolvedClass
from .timetable_slot_serialiser import TimetableSlot

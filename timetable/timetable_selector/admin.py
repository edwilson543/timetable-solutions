from django.contrib import admin
from .models import Pupil, Teacher, Classroom, FixedClass, TimetableSlot

admin.site.register(Pupil)
admin.site.register(Teacher)
admin.site.register(Classroom)
admin.site.register(FixedClass)
admin.site.register(TimetableSlot)

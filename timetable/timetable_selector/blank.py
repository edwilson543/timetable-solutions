import datetime as dt
from django.db import models
t = dt.time(5, 30)

print(t)


class PeriodStart(dt.time, models.Choices):
    PERIOD_ONE = 1, 2, "p1"


print(PeriodStart.choices)
print(PeriodStart.values)

print(dt.timedelta(hours=1))
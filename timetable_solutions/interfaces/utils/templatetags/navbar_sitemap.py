"""Template tag and ancillaries for storing the sitemap."""

# Standard library imports
import dataclasses

# Django imports
from django import template

# Local application imports
from interfaces.constants import UrlName


@dataclasses.dataclass(frozen=True)
class Page:
    """A single page on the site, accessible via the sitemap."""

    name: str
    url: str
    fa_icon: str  # e.g. "fa-regular fa-calendar-days"


@dataclasses.dataclass(frozen=True)
class PageCollection:
    """A collection of pages, with some other meta-info"""

    name: str
    pages: list[Page]
    fa_icon: str  # e.g. "fa-regular fa-calendar-days"


register = template.Library()


@register.simple_tag
def sitemap() -> list[PageCollection]:
    """
    Define the core site contents for rendering in html (e.g. in the navbar).
    Does not include any urls that require kwargs.
    """
    return [
        PageCollection(
            name="Basic data",
            fa_icon="fa-solid fa-graduation-cap",
            pages=[
                Page(
                    "Teachers",
                    url=UrlName.TEACHER_LANDING_PAGE.url(),
                    fa_icon="fa-solid fa-person-chalkboard",
                ),
                Page(
                    "Classrooms",
                    url=UrlName.CLASSROOM_LANDING_PAGE.url(),
                    fa_icon="fa-solid fa-school",
                ),
                Page(
                    "Year groups",
                    url=UrlName.YEAR_GROUP_LANDING_PAGE.url(),
                    fa_icon="fa-solid fa-children",
                ),
                Page(
                    "Timetable slots",
                    url=UrlName.TIMETABLE_SLOT_LANDING_PAGE.url(),
                    fa_icon="fa-solid fa-clock",
                ),
                Page(
                    "Breaks",
                    url=UrlName.BREAK_LANDING_PAGE.url(),
                    fa_icon="fa-solid fa-baseball-bat-ball",
                ),
                Page(
                    "Pupils",
                    url=UrlName.PUPIL_LANDING_PAGE.url(),
                    fa_icon="fa-solid fa-child",
                ),
                Page(
                    "Lessons",
                    url=UrlName.LESSON_LANDING_PAGE.url(),
                    fa_icon="fa-solid fa-brain",
                ),
            ],
        ),
        PageCollection(
            name="Timetables",
            fa_icon="fa-regular fa-calendar-days",
            pages=[
                Page(
                    "Create timetables",
                    url=UrlName.CREATE_TIMETABLES.url(),
                    fa_icon="fa-solid fa-puzzle-piece",
                ),
                Page(
                    "Pupil timetables",
                    url=UrlName.PUPIL_LIST.url(),
                    fa_icon="fa-solid fa-child",
                ),
                Page(
                    "Teacher timetables",
                    url=UrlName.TEACHER_LIST.url(),
                    fa_icon="fa-solid fa-person-chalkboard",
                ),
            ],
        ),
        PageCollection(
            name="Users",
            fa_icon="fa-solid fa-user",
            pages=[
                Page(
                    "Manage users",
                    url=UrlName.USER_LIST.url(),
                    fa_icon="fa-solid fa-user-gear",
                )
            ],
        ),
    ]

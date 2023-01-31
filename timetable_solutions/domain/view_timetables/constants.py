"""Constants relating to viewing timetables."""


# Display name for a free period TimetableComponent
FREE = "Free"


class Colour:
    """Colours for timetable components that are not lessons"""

    BREAK = "#b3b3b3"  # Light grey
    FREE = "#feffba"  # Yellow

    _colour_ranking: dict[int, str] = {
        0: "#ffbfd6",  # Pale red
        1: "#c8d4e3",  # Pale blue
        2: "#b3f2b3",  # Pale green
        3: "#d0bad6",  # Lilac
        4: "#e3ad62",  # Pale orange
        5: "#675fb0",  # Dark blue
        6: "#aabf5e",  # Muddy green
        7: "#8f7e78",  # Pink-grey
        8: "#d18771",  # Dark red
        9: "#169c6f",  # Turquoise
        10: "#c9ae61",  # Light brown
    }

    @classmethod
    def get_colour(cls, rank: int) -> str:
        """
        Get colour by rank, or modulus rank.
        Meaning the colours are unique when a timetable has fewer than x distinct lessons.
        """
        rank = rank % cls.rank_modulo()
        return cls._colour_ranking[rank]

    @classmethod
    def rank_modulo(cls) -> int:
        # 1 ensures the highest rank colour gets used
        return max(cls._colour_ranking.keys()) + 1

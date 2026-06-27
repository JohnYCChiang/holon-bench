from dataclasses import dataclass


@dataclass(frozen=True)
class Interval:
    start: int
    end: int

    def overlaps(self, other: "Interval") -> bool:
        raise NotImplementedError("implement Interval.overlaps per DOMAIN.md")


class Calendar:
    """Aggregate root for one resource. Reservations may not overlap."""

    def __init__(self):
        self.reservations: list[Interval] = []

    def book(self, start: int, end: int) -> None:
        raise NotImplementedError("implement Calendar.book per DOMAIN.md")

    def is_free(self, start: int, end: int) -> bool:
        raise NotImplementedError("implement Calendar.is_free per DOMAIN.md")

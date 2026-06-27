from dataclasses import dataclass


@dataclass(frozen=True)
class TimeSlot:
    start: int
    end: int

    def __post_init__(self):
        if self.start >= self.end:
            raise ValueError("start must be before end")

    def overlaps(self, other: "TimeSlot") -> bool:
        raise NotImplementedError("implement TimeSlot.overlaps per DOMAIN.md")


class Room:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.bookings: list = []

    def book(self, slot: "TimeSlot", attendees: int) -> None:
        raise NotImplementedError("implement Room.book per DOMAIN.md")

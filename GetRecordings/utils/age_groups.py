from enum import Enum


class AgeGroups(Enum):
    KIDS = "kids"
    TEENS = "teens"
    ADULTS = "adults"
    ALL = "all"

    def __str__(self):
        return self.value

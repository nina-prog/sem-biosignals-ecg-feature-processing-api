from enum import Enum


class SignalEnum(str, Enum):
    chest = 'chest'
    wrest = 'wrest'


class WindowSlicingMethodEnum(str, Enum):
    time_related = 'time_related'
    label_related_before = 'label_related_before'
    label_related_after = 'label_related_after'
    label_related_middle = 'label_related_centered'

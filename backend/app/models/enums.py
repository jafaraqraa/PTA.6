from enum import Enum


class EarSideEnum(str, Enum):
    LEFT = "left"
    RIGHT = "right"


class TestTypeEnum(str, Enum):
    AC = "AC"
    AC_MASKED = "AC_masked"
    BC = "BC"
    BC_MASKED = "BC_masked"


class ResponseEnum(str, Enum):
    HEARD = "heard"
    NOT_HEARD = "not_heard"


class HearingTypeEnum(str, Enum):
    NORMAL = "Normal"
    CONDUCTIVE = "Conductive"
    SENSORINEURAL = "Sensorineural"
    MIXED = "Mixed"


class HearingSeverityEnum(str, Enum):
    NORMAL = "Normal"
    MILD = "Mild"
    MODERATE = "Moderate"
    MODERATELY_SEVERE = "Moderately Severe"
    SEVERE = "Severe"
    PROFOUND = "Profound"
    UNDETERMINED = "Undetermined"


class HearingConfigurationEnum(str, Enum):
    ALL_FREQUENCIES = "All Frequencies"
    LOW_FREQUENCIES = "Low Frequencies"
    MID_FREQUENCIES = "Mid Frequencies"
    HIGH_FREQUENCIES = "High Frequencies"
    SINGLE_FREQUENCY = "Single Frequency"
    NOTCH_PATTERN = "Notch Pattern"
    OTHER = "Other"
    UNDETERMINED = "Undetermined"


HearingDistributionEnum = HearingConfigurationEnum


class PatientSourceEnum(str, Enum):
    REAL = "real"
    SYNTHETIC = "synthetic"


# ================================
# إضافات مرتبطة بالـ Audiogram
# ================================

class FrequencyEnum(int, Enum):
    F125 = 125
    F250 = 250
    F500 = 500
    F750 = 750
    F1000 = 1000
    F1500 = 1500
    F2000 = 2000
    F3000 = 3000
    F4000 = 4000
    F6000 = 6000
    F8000 = 8000

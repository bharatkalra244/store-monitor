from djchoices import ChoiceItem, DjangoChoices

class WeekDayType(DjangoChoices):
    MONDAY = ChoiceItem(0, "Monday")
    TUESDAY = ChoiceItem(1, "Tuesday")
    WEDNESDAY = ChoiceItem(2, "Wednesday")
    THURSDAY = ChoiceItem(3, "Thursday")
    FRIDAY = ChoiceItem(4, "Friday")
    SATURDAY = ChoiceItem(5, "Saturday")
    SUNDAY = ChoiceItem(6, "Sunday")
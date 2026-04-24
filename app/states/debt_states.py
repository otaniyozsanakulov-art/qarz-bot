from aiogram.fsm.state import StatesGroup, State


class DebtState(StatesGroup):
    entering_name = State()
    entering_amount = State()
    choosing_currency = State()
    choosing_type = State()
    entering_taken_date = State()
    entering_due_date = State()
    entering_note = State()
    choosing_save_type = State()
    entering_other_username = State()

class ReportState(StatesGroup):
    choosing_direction = State()
    choosing_type = State()
    entering_search = State()
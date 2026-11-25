from pipecat.services.llm_service import FunctionCallParams

from app.appointment_tools import (
    check_doctor_availability as check_availability,
    book_appointment as create_booking,
    cancel_appointment as cancel_booking
)


async def check_doctor_availability(
    params: FunctionCallParams,
    speciality: str = "",
    appointment_date: str = ""
):
    """Find available doctors and appointment slots.

    Args:
        speciality: Medical speciality, such as Cardiology.
        appointment_date: Requested date in YYYY-MM-DD format.
    """

    result = check_availability(
        speciality=speciality or None,
        appointment_date=appointment_date or None
    )

    await params.result_callback(result)


async def book_appointment(
    params: FunctionCallParams,
    phone_number: str,
    slot_id: str
):
    """Book an appointment after the caller confirms their phone number.

    Args:
        phone_number: Phone number confirmed by the caller.
        slot_id: Identifier of the selected available slot.
    """

    result = create_booking(
        phone_number=phone_number,
        slot_id=slot_id
    )

    await params.result_callback(result)


async def cancel_appointment(
    params: FunctionCallParams,
    phone_number: str,
    appointment_id: int
):
    """Cancel an existing appointment after caller verification.

    Args:
        phone_number: Phone number confirmed by the caller.
        appointment_id: Identifier of the appointment to cancel.
    """

    result = cancel_booking(
        phone_number=phone_number,
        appointment_id=appointment_id
    )

    await params.result_callback(result)
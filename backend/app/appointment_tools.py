# backend/app/appointment_tools.py

from app.database import (
    get_available_slots,
    create_appointment,
    get_appointments_by_phone,
    cancel_appointment as db_cancel_appointment
)


# ==========================================
# TOOL 1: CHECK DOCTOR AVAILABILITY
# ==========================================

def check_doctor_availability(
    speciality: str = None,
    appointment_date: str = None
):
    """
    Find available doctors and appointment slots.

    Args:
        speciality: Medical speciality requested by caller.
        appointment_date: Date in YYYY-MM-DD format.

    Returns:
        Available doctors and their appointment slots.
    """

    try:

        slots = get_available_slots(
            speciality=speciality,
            appointment_date=appointment_date
        )

        if not slots:
            return {
                "success": True,
                "message": "No available appointment slots found.",
                "slots": []
            }

        return {
            "success": True,
            "message": f"Found {len(slots)} available slots.",
            "slots": slots
        }

    except Exception as error:

        return {
            "success": False,
            "message": str(error),
            "slots": []
        }


# ==========================================
# TOOL 2: BOOK APPOINTMENT
# ==========================================

def book_appointment(
    phone_number: str,
    slot_id: str
):
    """
    Book an available appointment for a caller.

    Args:
        phone_number: Phone number spoken by caller.
        slot_id: ID of the selected appointment slot.

    Returns:
        Appointment confirmation details.
    """

    try:

        if not phone_number or not slot_id:
            return {
                "success": False,
                "message": "Phone number and slot ID are required."
            }

        result = create_appointment(
            phone_number=phone_number,
            slot_id=slot_id
        )

        return {
            "success": True,
            "message": "Appointment booked successfully.",
            "appointment": result
        }

    except ValueError as error:

        return {
            "success": False,
            "message": str(error)
        }

    except Exception:

        return {
            "success": False,
            "message": "Unable to book appointment due to a system error."
        }


# ==========================================
# TOOL 3: CANCEL APPOINTMENT
# ==========================================

def cancel_appointment(
    phone_number: str,
    appointment_id: int
):
    """
    Cancel an existing appointment.

    Args:
        phone_number: Phone number spoken by caller.
        appointment_id: ID of the appointment to cancel.

    Returns:
        Cancellation confirmation.
    """

    try:

        if not phone_number or not appointment_id:
            return {
                "success": False,
                "message": "Phone number and appointment ID are required."
            }

        # Verify the caller owns this appointment
        appointments = get_appointments_by_phone(
            phone_number
        )

        matching_appointment = next(
            (
                appointment
                for appointment in appointments
                if appointment["appointment_id"] == appointment_id
                and appointment["status"] == "booked"
            ),
            None
        )

        if matching_appointment is None:
            return {
                "success": False,
                "message": "No active appointment found for this caller."
            }

        result = db_cancel_appointment(
            phone_number=phone_number,
            appointment_id=appointment_id
        )

        return {
            "success": True,
            "message": "Appointment cancelled successfully.",
            "appointment": result
        }

    except ValueError as error:

        return {
            "success": False,
            "message": str(error)
        }

    except Exception:

        return {
            "success": False,
            "message": "Unable to cancel appointment due to a system error."
        }
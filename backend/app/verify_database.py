from datetime import date

from app.seed_data import seed_database

from app.database import (
    get_doctors,
    get_available_slots,
    create_appointment,
    get_appointments_by_phone,
    cancel_appointment
)


def verify_database():

    # Step 1: Populate database
    seed_database()

    # Step 2: Retrieve doctors
    doctors = get_doctors()

    print("\nDOCTORS:")
    for doctor in doctors:
        print(doctor)

    assert len(doctors) == 3


    # Step 3: Find available slots
    today = date.today().isoformat()

    slots = get_available_slots(
        speciality="Cardiology",
        appointment_date=today
    )

    print("\nAVAILABLE SLOTS:")
    for slot in slots:
        print(slot)

    assert len(slots) > 0


    # Step 4: Book an appointment
    selected_slot = slots[0]

    booking = create_appointment(
        phone_number="9999999999",
        slot_id=selected_slot["slot_id"]
    )

    print("\nBOOKING RESULT:")
    print(booking)

    assert booking["success"] is True


    # Step 5: Verify appointment
    appointments = get_appointments_by_phone(
        "9999999999"
    )

    print("\nCALLER APPOINTMENTS:")
    print(appointments)

    assert len(appointments) == 1
    assert appointments[0]["status"] == "booked"


    # Step 6: Verify booked slot is unavailable
    remaining_slots = get_available_slots(
        speciality="Cardiology",
        appointment_date=today
    )

    assert all(
        slot["slot_id"] != selected_slot["slot_id"]
        for slot in remaining_slots
    )


    # Step 7: Cancel appointment
    cancellation = cancel_appointment(
        phone_number="9999999999",
        appointment_id=booking["appointment_id"]
    )

    print("\nCANCELLATION RESULT:")
    print(cancellation)

    assert cancellation["success"] is True


    # Step 8: Verify slot is available again
    restored_slots = get_available_slots(
        speciality="Cardiology",
        appointment_date=today
    )

    assert any(
        slot["slot_id"] == selected_slot["slot_id"]
        for slot in restored_slots
    )

    print("\nALL DATABASE TESTS PASSED!")


if __name__ == "__main__":
    verify_database()
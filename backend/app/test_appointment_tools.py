# backend/app/test_appointment_tools.py

from app.seed_data import seed_database

from app.database import get_available_slots

from app.appointment_tools import (
    check_doctor_availability,
    book_appointment,
    cancel_appointment
)


def test_appointment_tools():

    print("\n========== STEP 1: INITIALIZE ==========")

    seed_database()


    # ----------------------------------
    # TEST 1: CHECK AVAILABILITY
    # ----------------------------------

    print("\n========== TEST 1: AVAILABILITY ==========")

    availability = check_doctor_availability(
        speciality="Cardiology"
    )

    print(availability)

    assert availability["success"] is True
    assert len(availability["slots"]) > 0

    selected_slot = availability["slots"][0]

    print("Availability test passed!")


    # ----------------------------------
    # TEST 2: BOOK APPOINTMENT
    # ----------------------------------

    print("\n========== TEST 2: BOOKING ==========")

    booking = book_appointment(
        phone_number="9876543210",
        slot_id=selected_slot["slot_id"]
    )

    print(booking)

    assert booking["success"] is True

    appointment_id = booking["appointment"]["appointment_id"]

    print("Booking test passed!")


    # ----------------------------------
    # TEST 3: PREVENT DOUBLE BOOKING
    # ----------------------------------

    print("\n========== TEST 3: DOUBLE BOOKING ==========")

    duplicate = book_appointment(
        phone_number="9123456780",
        slot_id=selected_slot["slot_id"]
    )

    print(duplicate)

    assert duplicate["success"] is False

    print("Double booking prevention passed!")


    # ----------------------------------
    # TEST 4: PREVENT WRONG CALLER CANCELLATION
    # ----------------------------------

    print("\n========== TEST 4: OWNERSHIP CHECK ==========")

    wrong_cancellation = cancel_appointment(
        phone_number="9999999999",
        appointment_id=appointment_id
    )

    print(wrong_cancellation)

    assert wrong_cancellation["success"] is False

    print("Caller ownership test passed!")


    # ----------------------------------
    # TEST 5: CANCEL APPOINTMENT
    # ----------------------------------

    print("\n========== TEST 5: CANCELLATION ==========")

    cancellation = cancel_appointment(
        phone_number="9876543210",
        appointment_id=appointment_id
    )

    print(cancellation)

    assert cancellation["success"] is True

    print("Cancellation test passed!")


    # ----------------------------------
    # TEST 6: VERIFY SLOT RELEASE
    # ----------------------------------

    print("\n========== TEST 6: SLOT RELEASE ==========")

    remaining_slots = get_available_slots(
        speciality="Cardiology"
    )

    slot_restored = any(
        slot["slot_id"] == selected_slot["slot_id"]
        for slot in remaining_slots
    )

    assert slot_restored is True

    print("Slot release test passed!")


    # ----------------------------------
    # TEST 7: PREVENT REPEATED CANCELLATION
    # ----------------------------------

    print("\n========== TEST 7: REPEATED CANCELLATION ==========")

    repeated_cancellation = cancel_appointment(
        phone_number="9876543210",
        appointment_id=appointment_id
    )

    assert repeated_cancellation["success"] is False

    print("Repeated cancellation prevention passed!")


    print("\n========================================")
    print("ALL APPOINTMENT TOOL TESTS PASSED!")
    print("========================================")


if __name__ == "__main__":
    test_appointment_tools()
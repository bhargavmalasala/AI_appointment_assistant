# backend/app/seed_data.py

from datetime import date, timedelta

from app.database import (
    get_connection,
    initialize_db
)


# ---------------------------------------
# 1. MOCK DOCTOR DATA
# ---------------------------------------

DOCTORS = [

    {
        "doctor_id": "DOC001",
        "name": "Dr. Sharma",
        "speciality": "Cardiology",
        "experience_years": 12
    },

    {
        "doctor_id": "DOC002",
        "name": "Dr. Reddy",
        "speciality": "Dermatology",
        "experience_years": 8
    },

    {
        "doctor_id": "DOC003",
        "name": "Dr. Mehta",
        "speciality": "Neurology",
        "experience_years": 15
    }

]


# ---------------------------------------
# 2. APPOINTMENT TIMINGS
# ---------------------------------------

TIME_SLOTS = [
    "09:00",
    "10:00",
    "11:00",
    "14:00",
    "15:00"
]


# ---------------------------------------
# 3. SEED DATABASE
# ---------------------------------------

def seed_database():

    initialize_db()

    connection = get_connection()

    try:

        # Insert doctors
        for doctor in DOCTORS:

            connection.execute("""

                INSERT OR IGNORE INTO doctors (
                    doctor_id,
                    name,
                    speciality,
                    experience_years
                )

                VALUES (?, ?, ?, ?)

            """, (
                doctor["doctor_id"],
                doctor["name"],
                doctor["speciality"],
                doctor["experience_years"]
            ))


        # Generate slots for the next 7 days
        today = date.today()

        for doctor in DOCTORS:

            for day in range(7):

                appointment_date = (
                    today + timedelta(days=day)
                ).isoformat()

                for time in TIME_SLOTS:

                    slot_id = (
                        f'{doctor["doctor_id"]}-'
                        f'{appointment_date.replace("-", "")}-'
                        f'{time.replace(":", "")}'
                    )

                    connection.execute("""

                        INSERT OR IGNORE INTO slots (
                            slot_id,
                            doctor_id,
                            appointment_date,
                            start_time,
                            status
                        )

                        VALUES (?, ?, ?, ?, 'available')

                    """, (
                        slot_id,
                        doctor["doctor_id"],
                        appointment_date,
                        time
                    ))


        connection.commit()

        print("Database seeded successfully!")

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()


# ---------------------------------------
# 4. EXECUTION
# ---------------------------------------

if __name__ == "__main__":

    seed_database()
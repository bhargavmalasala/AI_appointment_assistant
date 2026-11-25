# backend/app/database.py

import sqlite3
from pathlib import Path
from datetime import datetime, timezone


# Database file location
DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "appointments.db"
)


# ---------------------------------------
# 1. DATABASE CONNECTION
# ---------------------------------------

def get_connection():
    """
    Creates and returns a connection to SQLite.
    """

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        DB_PATH,
        timeout=10
    )

    connection.row_factory = sqlite3.Row

    # Enable foreign key validation
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ---------------------------------------
# 2. DATABASE INITIALIZATION
# ---------------------------------------

def initialize_db():
    """
    Creates all required tables and indexes.
    """

    connection = get_connection()

    try:
        connection.executescript("""

            CREATE TABLE IF NOT EXISTS doctors (

                doctor_id TEXT PRIMARY KEY,

                name TEXT NOT NULL,

                speciality TEXT NOT NULL,

                experience_years INTEGER NOT NULL
                CHECK (experience_years >= 0)

            );


            CREATE TABLE IF NOT EXISTS slots (

                slot_id TEXT PRIMARY KEY,

                doctor_id TEXT NOT NULL,

                appointment_date TEXT NOT NULL,

                start_time TEXT NOT NULL,

                status TEXT NOT NULL DEFAULT 'available'
                CHECK (status IN ('available', 'booked')),

                FOREIGN KEY (doctor_id)
                REFERENCES doctors(doctor_id),

                UNIQUE (
                    doctor_id,
                    appointment_date,
                    start_time
                )

            );


            CREATE TABLE IF NOT EXISTS appointments (

                appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,

                phone_number TEXT NOT NULL,

                doctor_id TEXT NOT NULL,

                slot_id TEXT NOT NULL,

                status TEXT NOT NULL DEFAULT 'booked'
                CHECK (status IN ('booked', 'cancelled')),

                created_at TEXT NOT NULL,

                cancelled_at TEXT,

                FOREIGN KEY (doctor_id)
                REFERENCES doctors(doctor_id),

                FOREIGN KEY (slot_id)
                REFERENCES slots(slot_id)

            );


            CREATE UNIQUE INDEX IF NOT EXISTS
            unique_active_appointment_per_slot
            ON appointments(slot_id)
            WHERE status = 'booked';


            CREATE INDEX IF NOT EXISTS
            idx_appointments_phone
            ON appointments(phone_number, status);

        """)

        connection.commit()

    finally:
        connection.close()


# ---------------------------------------
# 3. GET ALL DOCTORS
# ---------------------------------------

def get_doctors():
    """
    Returns all doctors stored in the database.
    """

    connection = get_connection()

    try:
        doctors = connection.execute("""

            SELECT *
            FROM doctors
            ORDER BY name

        """).fetchall()

        return [dict(doctor) for doctor in doctors]

    finally:
        connection.close()


# ---------------------------------------
# 4. CHECK AVAILABLE SLOTS
# ---------------------------------------

def get_available_slots(speciality=None, appointment_date=None):
    """
    Returns available slots.

    Filters:
    - Doctor speciality (optional)
    - Appointment date (optional)
    """

    connection = get_connection()

    try:

        query = """

            SELECT
                s.slot_id,
                s.appointment_date,
                s.start_time,
                s.status,
                d.doctor_id,
                d.name AS doctor_name,
                d.speciality,
                d.experience_years

            FROM slots s

            JOIN doctors d
            ON s.doctor_id = d.doctor_id

            WHERE s.status = 'available'

        """

        parameters = []

        if speciality:
            query += " AND LOWER(d.speciality) = LOWER(?)"
            parameters.append(speciality.strip())

        if appointment_date:
            query += " AND s.appointment_date = ?"
            parameters.append(appointment_date)

        query += " ORDER BY s.appointment_date, s.start_time"

        slots = connection.execute(
            query,
            parameters
        ).fetchall()

        return [dict(slot) for slot in slots]

    finally:
        connection.close()


# ---------------------------------------
# 5. NORMALIZE PHONE NUMBER
# ---------------------------------------

def normalize_phone_number(phone_number):
    """
    Removes spaces and formatting characters
    from the phone number.
    """

    if not isinstance(phone_number, str):
        raise ValueError("Phone number must be text.")

    normalized = "".join(
        character
        for character in phone_number
        if character.isdigit()
    )

    if not 7 <= len(normalized) <= 15:
        raise ValueError("Invalid phone number.")

    return normalized


# ---------------------------------------
# 6. BOOK AN APPOINTMENT
# ---------------------------------------

def create_appointment(phone_number, slot_id):
    """
    Books an available slot for a caller.
    """

    phone_number = normalize_phone_number(phone_number)

    connection = get_connection()

    try:

        # Prevent concurrent bookings of the same slot
        connection.execute("BEGIN IMMEDIATE")

        slot = connection.execute("""

            SELECT *
            FROM slots
            WHERE slot_id = ?
            AND status = 'available'

        """, (slot_id,)).fetchone()

        if slot is None:
            raise ValueError("Slot does not exist or is unavailable.")

        # Reserve the slot
        result = connection.execute("""

            UPDATE slots
            SET status = 'booked'
            WHERE slot_id = ?
            AND status = 'available'

        """, (slot_id,))

        if result.rowcount != 1:
            raise ValueError("Slot is no longer available.")

        # Create appointment record
        cursor = connection.execute("""

            INSERT INTO appointments (
                phone_number,
                doctor_id,
                slot_id,
                status,
                created_at
            )

            VALUES (?, ?, ?, 'booked', ?)

        """, (
            phone_number,
            slot["doctor_id"],
            slot_id,
            datetime.now(timezone.utc).isoformat()
        ))

        appointment_id = cursor.lastrowid

        connection.commit()

        return {
            "success": True,
            "appointment_id": appointment_id,
            "phone_number": phone_number,
            "doctor_id": slot["doctor_id"],
            "slot_id": slot_id,
            "date": slot["appointment_date"],
            "time": slot["start_time"],
            "status": "booked"
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ---------------------------------------
# 7. FIND CALLER APPOINTMENTS
# ---------------------------------------

def get_appointments_by_phone(phone_number):
    """
    Finds appointments belonging to a phone number.
    Includes booked and cancelled records.
    """

    phone_number = normalize_phone_number(phone_number)

    connection = get_connection()

    try:

        appointments = connection.execute("""

            SELECT
                a.appointment_id,
                a.phone_number,
                a.status,
                a.created_at,
                a.cancelled_at,

                d.doctor_id,
                d.name AS doctor_name,
                d.speciality,

                s.slot_id,
                s.appointment_date,
                s.start_time

            FROM appointments a

            JOIN doctors d
            ON a.doctor_id = d.doctor_id

            JOIN slots s
            ON a.slot_id = s.slot_id

            WHERE a.phone_number = ?

            ORDER BY a.appointment_id DESC

        """, (phone_number,)).fetchall()

        return [dict(appointment) for appointment in appointments]

    finally:
        connection.close()


# ---------------------------------------
# 8. CANCEL AN APPOINTMENT
# ---------------------------------------

def cancel_appointment(phone_number, appointment_id):
    """
    Cancels a caller's active appointment
    and releases its slot.
    """

    phone_number = normalize_phone_number(phone_number)

    connection = get_connection()

    try:

        connection.execute("BEGIN IMMEDIATE")

        appointment = connection.execute("""

            SELECT *
            FROM appointments

            WHERE appointment_id = ?
            AND phone_number = ?
            AND status = 'booked'

        """, (
            appointment_id,
            phone_number
        )).fetchone()

        if appointment is None:
            raise ValueError(
                "No active appointment found for this phone number."
            )

        # Mark appointment as cancelled
        connection.execute("""

            UPDATE appointments

            SET status = 'cancelled',
                cancelled_at = ?

            WHERE appointment_id = ?

        """, (
            datetime.now(timezone.utc).isoformat(),
            appointment_id
        ))

        # Release the previously booked slot
        connection.execute("""

            UPDATE slots

            SET status = 'available'

            WHERE slot_id = ?

        """, (appointment["slot_id"],))

        connection.commit()

        return {
            "success": True,
            "appointment_id": appointment_id,
            "phone_number": phone_number,
            "status": "cancelled",
            "message": "Appointment cancelled successfully."
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
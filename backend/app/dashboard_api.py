
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Query

from pipecat.runner.run import app

from app.database import (
    get_connection,
    get_doctors,
    get_available_slots,
)


# Allow the React + Vite frontend to access the backend API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/api/doctors")
async def doctors():
    return get_doctors()


@app.get("/api/slots")
async def available_slots(
    speciality: str | None = Query(default=None),
    appointment_date: str | None = Query(default=None),
):
    return get_available_slots(
        speciality=speciality,
        appointment_date=appointment_date,
    )


@app.get("/api/appointments")
async def appointments():
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                a.appointment_id,
                a.phone_number,
                a.status,
                d.doctor_id,
                d.name AS doctor_name,
                d.speciality,
                s.slot_id,
                s.appointment_date,
                s.start_time
            FROM appointments a
            JOIN slots s ON a.slot_id = s.slot_id
            JOIN doctors d ON s.doctor_id = d.doctor_id
            ORDER BY a.appointment_id DESC
            """
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


@app.get("/api/stats")
async def dashboard_stats():
    doctors_list = get_doctors()
    slots_list = get_available_slots()

    connection = get_connection()

    try:
        total_appointments = connection.execute(
            "SELECT COUNT(*) FROM appointments"
        ).fetchone()[0]

        booked_appointments = connection.execute(
            "SELECT COUNT(*) FROM appointments WHERE status = 'booked'"
        ).fetchone()[0]

        cancelled_appointments = connection.execute(
            "SELECT COUNT(*) FROM appointments WHERE status = 'cancelled'"
        ).fetchone()[0]

        return {
            "total_doctors": len(doctors_list),
            "available_slots": len(slots_list),
            "total_appointments": total_appointments,
            "booked_appointments": booked_appointments,
            "cancelled_appointments": cancelled_appointments,
        }

    finally:
        connection.close()

import { useEffect, useRef, useState } from "react";
import VoiceAssistant from "./components/VoiceAssistant";
import "./index.css";
import "./App.css";

const API_BASE = "http://localhost:7860/api";

function App() {
  const [theme, setTheme] = useState(
    () => localStorage.getItem("careconnect-theme") || "light",
  );

  useEffect(() => {
    localStorage.setItem("careconnect-theme", theme);
  }, [theme]);

  const [doctors, setDoctors] = useState([]);
  const [slots, setSlots] = useState([]);
  const [showAllSlots, setShowAllSlots] = useState(false);
  const [appointments, setAppointments] = useState([]);
  const [highlightedAppointmentId, setHighlightedAppointmentId] =
    useState(null);

  const [bookingConfirmation, setBookingConfirmation] = useState(null);
  const previousAppointmentsRef = useRef(new Map());
  const hasLoadedAppointmentsRef = useRef(false);

  const [stats, setStats] = useState({
    total_doctors: 0,
    available_slots: 0,
    total_appointments: 0,
  });
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    const fetchDashboardData = async () => {
      try {
        const [doctorsRes, slotsRes, appointmentsRes, statsRes] =
          await Promise.all([
            fetch(`${API_BASE}/doctors`),
            fetch(`${API_BASE}/slots`),
            fetch(`${API_BASE}/appointments`),
            fetch(`${API_BASE}/stats`),
          ]);

        if (
          !doctorsRes.ok ||
          !slotsRes.ok ||
          !appointmentsRes.ok ||
          !statsRes.ok
        ) {
          throw new Error("Could not load dashboard data.");
        }

        const [doctorsData, slotsData, appointmentsData, statsData] =
          await Promise.all([
            doctorsRes.json(),
            slotsRes.json(),
            appointmentsRes.json(),
            statsRes.json(),
          ]);

        if (!active) return;

        // Build a lookup of previously known appointments.
        const currentAppointmentsMap = new Map(
          appointmentsData.map((appointment) => [
            String(appointment.appointment_id),
            appointment,
          ]),
        );

        // detection of new bookings and cancellations
        const previousAppointments = previousAppointmentsRef.current;

        if (hasLoadedAppointmentsRef.current) {
          const changedAppointment = appointmentsData.find((appointment) => {
            const previous = previousAppointments.get(
              String(appointment.appointment_id),
            );

            return (
              previous &&
              previous.status === "booked" &&
              appointment.status === "cancelled"
            );
          });

          const newBooking = appointmentsData.find((appointment) => {
            return (
              appointment.status === "booked" &&
              !previousAppointments.has(String(appointment.appointment_id))
            );
          });

          if (changedAppointment) {
            setHighlightedAppointmentId(changedAppointment.appointment_id);
            setBookingConfirmation({
              type: "cancelled",
              appointmentId: changedAppointment.appointment_id,
              doctorName: changedAppointment.doctor_name,
              speciality: changedAppointment.speciality,
              date: changedAppointment.appointment_date,
              time: changedAppointment.start_time,
            });
          } else if (newBooking) {
            setHighlightedAppointmentId(newBooking.appointment_id);
            setBookingConfirmation({
              type: "booked",
              appointmentId: newBooking.appointment_id,
              doctorName: newBooking.doctor_name,
              speciality: newBooking.speciality,
              date: newBooking.appointment_date,
              time: newBooking.start_time,
            });
          }
        }

        

        hasLoadedAppointmentsRef.current = true;

        previousAppointmentsRef.current = currentAppointmentsMap;

        setDoctors(doctorsData);
        setSlots(slotsData);
        setAppointments(appointmentsData);
        setStats(statsData);
        setError("");
      } catch (err) {
        if (active) {
          setError(err.message || "Unable to connect to backend.");
        }
      }
    };

    fetchDashboardData();

    // Refresh data so voice bookings and cancellations appear automatically.
    const interval = setInterval(fetchDashboardData, 3000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  const visibleSlots = showAllSlots ? slots : slots.slice(0, 5);

  return (
    <div className="app" data-theme={theme}>
      <main className="dashboard">
        <header className="dashboard-header">
          <div className="brand">
            <div className="brand-icon">✚</div>
            <div>
              <h1>CareConnect</h1>
              <p>AI Doctor Appointment Assistant</p>
            </div>
          </div>

          <div className="dashboard-date">
            {new Date().toLocaleDateString("en-IN", {
              weekday: "long",
              day: "numeric",
              month: "long",
              year: "numeric",
            })}
          </div>
          <button
            className="theme-toggle"
            onClick={() =>
              setTheme((current) => (current === "light" ? "dark" : "light"))
            }
            aria-label="Toggle colour theme"
            title="Toggle light and dark theme"
          >
            {theme === "light" ? "☾" : "☀"}
            {/* <span>{theme === "light" ? "Dark mode" : "Light mode"}</span> */}
          </button>
        </header>

        {error && <p className="dashboard-error">{error}</p>}

        <section className="overview-grid">
          <div className="overview-card">
            <p>Total Doctors</p>
            <h2>{stats.total_doctors}</h2>
          </div>

          <div className="overview-card">
            <p>Available Slots</p>
            <h2>{stats.available_slots}</h2>
          </div>

          <div className="overview-card">
            <p>Total Appointments</p>
            <h2>{stats.total_appointments}</h2>
          </div>
        </section>

        <div className="dashboard-grid">
          <div className="dashboard-main">
            <section className="dashboard-section">
              <div className="section-heading">
                <div>
                  <h2>Our Doctors</h2>
                  <p>Doctors and their specialities</p>
                </div>
              </div>

              <div className="doctor-list">
                {doctors.length === 0 ? (
                  <div className="doctor-card">
                    <p>No doctors found.</p>
                  </div>
                ) : (
                  doctors.map((doctor) => (
                    <div className="doctor-card" key={doctor.doctor_id}>
                      <h3>{doctor.name}</h3>
                      <p>{doctor.speciality}</p>
                    </div>
                  ))
                )}
              </div>
            </section>

            <section className="dashboard-section">
              <div className="section-heading">
                <div>
                  <h2>Available Slots</h2>
                  <p>Currently available appointment times</p>
                </div>
              </div>

              <div className="table-wrapper">
                <table className="appointments-table">
                  <thead>
                    <tr>
                      <th>Doctor</th>
                      <th>Speciality</th>
                      <th>Date</th>
                      <th>Time</th>
                    </tr>
                  </thead>

                  <tbody>
                    {slots.length === 0 ? (
                      <tr>
                        <td colSpan="4">No available slots.</td>
                      </tr>
                    ) : (
                      visibleSlots.map((slot) => (
                        <tr key={slot.slot_id}>
                          <td>{slot.doctor_name}</td>
                          <td>{slot.speciality}</td>
                          <td>{slot.appointment_date}</td>
                          <td>{slot.start_time}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>

                {slots.length > 5 && (
                  <button
                    className="show-slots-button"
                    onClick={() => setShowAllSlots((current) => !current)}
                  >
                    {showAllSlots
                      ? "Show less ↑"
                      : `Show all ${slots.length} slots ↓`}
                  </button>
                )}
              </div>
            </section>

            <section className="dashboard-section">
              <div className="section-heading">
                <div>
                  <h2>Appointments</h2>
                  <p>Recent patient appointments</p>
                </div>
              </div>

              <div className="table-wrapper">
                <table className="appointments-table">
                  <thead>
                    <tr>
                      <th>Appointment ID</th>
                      <th>Patient Phone</th>
                      <th>Doctor</th>
                      <th>Date</th>
                      <th>Time</th>
                      <th>Status</th>
                    </tr>
                  </thead>

                  <tbody>
                    {appointments.length === 0 ? (
                      <tr>
                        <td colSpan="6">No appointments found.</td>
                      </tr>
                    ) : (
                      appointments.map((appointment) => (
                        <tr
                          key={appointment.appointment_id}
                          className={
                            String(highlightedAppointmentId) ===
                            String(appointment.appointment_id)
                              ? "appointment-highlight"
                              : ""
                          }
                        >
                          <td>{appointment.appointment_id}</td>
                          <td>{appointment.phone_number}</td>
                          <td>{appointment.doctor_name}</td>
                          <td>{appointment.appointment_date}</td>
                          <td>{appointment.start_time}</td>
                          <td>
                            <span
                              className={`appointment-status ${
                                appointment.status === "booked"
                                  ? "status-booked"
                                  : "status-cancelled"
                              }`}
                            >
                              {appointment.status}
                            </span>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </section>
          </div>

          <aside className="dashboard-sidebar">
            <VoiceAssistant bookingConfirmation={bookingConfirmation} />
          </aside>
        </div>
      </main>
    </div>
  );
}

export default App;

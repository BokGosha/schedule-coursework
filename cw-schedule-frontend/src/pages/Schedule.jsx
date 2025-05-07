import React, { useEffect, useState } from "react";
import Calendar from "../components/Calendar";
import EventForm from "../components/EventForm";
import ScheduleService from "../services/ScheduleService";
import SharedScheduleService from "../services/SharedScheduleService";

const Schedule = () => {
    const [events, setEvents] = useState([]);
    const [openModal, setOpenModal] = useState(false);
    const [filteredEvents, setFilteredEvents] = useState([]);
    const [selectedDate, setSelectedDate] = useState(null);
    const [selectedColor, setSelectedColor] = useState(
        localStorage.getItem("selectedColor") || null
    );
    const [availableColors, setAvailableColors] = useState([]);
    const [formData, setFormData] = useState({
        title: "",
        description: "",
        start_time: new Date(),
        end_time: new Date(),
        is_all_day: false,
        location: "",
        color: "#3f51b5",
        is_recurring: false,
        recurrence_rule: "",
        category_id: null,
    });

    useEffect(() => {
        if (selectedColor) {
            setFilteredEvents(
                events.filter(
                    (event) => event.backgroundColor === selectedColor
                )
            );
        } else {
            setFilteredEvents(events);
        }
    }, [selectedColor, events]);

    useEffect(() => {
        fetchEvents();
    }, []);

    const fetchEvents = async () => {
        try {
            const schedules = await ScheduleService.getSchedules();

            const sharedSchedules =
                await SharedScheduleService.getSharedSchedulesWithMeWithData();

            const allEvents = [...schedules, ...sharedSchedules];

            const formattedEvents = allEvents.map((event) => ({
                id: event.id,
                title: event.title,
                start: event.start_time,
                end: event.end_time,
                allDay: event.is_all_day,
                backgroundColor: event.color,
                borderColor: event.color,
                textColor: "#ffffff",
                extendedProps: {
                    description: event.description,
                    location: event.location,
                    color: event.color,
                    isRecurring: event.is_recurring,
                    recurrenceRule: event.recurrence_rule,
                    categoryId: event.category_id,
                },
                ...(event.is_recurring && {
                    rrule: {
                        freq: event.recurrence_rule,
                        interval: 1,
                        dtstart: event.start_time,
                        byhour: [new Date(event.start_time).getUTCHours()], // Часы из UTC
                        byminute: [new Date(event.start_time).getUTCMinutes()], // Минуты из UTC
                    },
                    duration: `${durationInHours(
                        event.start_time,
                        event.end_time
                    )}`,
                }),
            }));

            setEvents(formattedEvents);

            const colors = [
                ...new Set(
                    formattedEvents.map((event) => event.backgroundColor)
                ),
            ];
            setAvailableColors(colors);
        } catch (error) {
            console.error("Ошибка загрузки событий:", error);
        }
    };

    const handleDateClick = (arg) => {
        setSelectedDate(arg.date);
        setFormData((prev) => ({
            ...prev,
            start_time: arg.date,
            end_time: new Date(arg.date.getTime() + 60 * 60 * 1000),
        }));
        setOpenModal(true);
    };

    const handleChange = (name, value) => {
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    function durationInHours(startISO, endISO) {
        const start = new Date(startISO);
        const end = new Date(endISO);
        const diffMs = end - start;

        const hours = Math.floor(diffMs / (1000 * 60 * 60));
        const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

        return `${hours}:${minutes.toString().padStart(2, "0")}`;
    }

    const handleSubmit = async () => {
        try {
            const createdEvent = await ScheduleService.createSchedule({
                ...formData,
                start_time: formData.start_time.toISOString(),
                end_time: formData.end_time.toISOString(),
            });

            fetchEvents();

            setOpenModal(false);

            return createdEvent;
        } catch (error) {
            console.error("Ошибка создания события:", error);
        }
    };

    return (
        <>
            <div className="color-selector">
                <div className="color-buttons">
                    <button
                        className={`color-button all-events ${
                            !selectedColor ? "selected" : ""
                        }`}
                        onClick={() => setSelectedColor(null)}
                    >
                        Все события
                    </button>
                    {availableColors.map((color) => (
                        <button
                            key={color}
                            className={`color-button color-option ${
                                selectedColor === color ? "selected" : ""
                            }`}
                            onClick={() => {
                                setSelectedColor(color);
                                localStorage.setItem("selectedColor", color);
                            }}
                            style={{
                                borderColor: color,
                                "--color": color,
                            }}
                        />
                    ))}
                </div>
            </div>

            <Calendar
                events={filteredEvents}
                handleDateClick={handleDateClick}
                refreshEvents={fetchEvents}
            />
            <EventForm
                open={openModal}
                onClose={() => setOpenModal(false)}
                formData={formData}
                onChange={handleChange}
                onSubmit={handleSubmit}
            />
        </>
    );
};

export default Schedule;

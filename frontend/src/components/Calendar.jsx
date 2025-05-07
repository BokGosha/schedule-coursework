import ruLocale from "@fullcalendar/core/locales/ru.js";
import dayGridPlugin from "@fullcalendar/daygrid/index.js";
import interactionPlugin from "@fullcalendar/interaction/index.js";
import FullCalendar from "@fullcalendar/react";
import rrulePlugin from "@fullcalendar/rrule/index.js";
import timeGridPlugin from "@fullcalendar/timegrid/index.js";
import React, { useEffect, useState } from "react";
import ScheduleService from "../services/ScheduleService";
import SharedScheduleService from "../services/SharedScheduleService";
import UserService from "../services/UserService";

const Calendar = ({ events, handleDateClick, refreshEvents }) => {
    const [selectedEvent, setSelectedEvent] = useState(null);
    const [editModalOpen, setEditModalOpen] = useState(false);
    const [eventData, setEventData] = useState({
        title: "",
        start: "",
        end: "",
        description: "",
        color: "",
    });
    const [owner, setOwner] = useState(null);
    const [isEventOwner, setIsEventOwner] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (editModalOpen && selectedEvent) {
            const loadData = async () => {
                setIsLoading(true);
                try {
                    const sharedSchedules =
                        await SharedScheduleService.getSharedSchedulesWithMeWithData();

                    const selectedEventInfo =
                        sharedSchedules.length == 0
                            ? await ScheduleService.getScheduleById(
                                  selectedEvent.id
                              )
                            : sharedSchedules.find(
                                  (schedule) =>
                                      schedule.id === parseInt(selectedEvent.id)
                              );

                    const isOwner =
                        parseInt(selectedEventInfo.user_id) ===
                        parseInt(UserService.getCurrentUser());

                    setIsEventOwner(isOwner);

                    if (!isOwner) {
                        const owner = await UserService.getUserById(
                            selectedEventInfo.user_id
                        );

                        setOwner(owner);
                    } else {
                        setOwner(null);
                    }
                } catch (error) {
                    console.error("Ошибка загрузки данных:", error);
                } finally {
                    setIsLoading(false);
                }
            };

            loadData();
        }
    }, [editModalOpen, selectedEvent]);

    const handleEventClick = (info) => {
        const event = info.event;
        console.log(event);

        setSelectedEvent(event);
        setEventData({
            title: event.title,
            start: event.start,
            end: event.end,
            description: event.extendedProps.description,
            color: event.backgroundColor,
        });
        setEditModalOpen(true);
    };

    const handleUpdateEvent = async () => {
        try {
            await ScheduleService.updateSchedule(selectedEvent.id, {
                title: eventData.title,
                start_time: eventData.start,
                description: eventData.description,
                end_time: eventData.end,
                color: eventData.color,
            });
            refreshEvents();
            setEditModalOpen(false);
        } catch (error) {
            console.error("Ошибка обновления события:", error);
        }
    };

    function formatForDateTimeLocal(date) {
        if (!date) return "";

        const offset = date.getTimezoneOffset() * 60000;
        const localDate = new Date(date.getTime() - offset);
        return localDate.toISOString().slice(0, 16);
    }

    function parseDateTimeLocal(datetimeString) {
        if (!datetimeString) return new Date();

        const utcString = `${datetimeString}:00.000Z`;
        const date = new Date(utcString);

        const offset = date.getTimezoneOffset() * 60000;
        return new Date(date.getTime() + offset);
    }

    const handleDeleteEvent = async () => {
        try {
            const sharedSchedules = [
                ...(await SharedScheduleService.getSharedSchedulesWithMe()),
                ...(await SharedScheduleService.getSharedSchedules()),
            ];

            const hasAccess = sharedSchedules.some(
                (schedule) =>
                    schedule.schedule_id === parseInt(selectedEvent.id)
            );

            const selectedSharedEvent = sharedSchedules.find(
                (schedule) =>
                    schedule.schedule_id === parseInt(selectedEvent.id)
            );

            if (hasAccess) {
                await SharedScheduleService.deleteSharedSchedule(
                    selectedSharedEvent.id
                );
            }

            await ScheduleService.deleteSchedule(selectedEvent.id);

            refreshEvents();

            setEditModalOpen(false);
        } catch (error) {
            console.error("Ошибка удаления события:", error);
        }
    };

    return (
        <>
            <FullCalendar
                plugins={[
                    dayGridPlugin,
                    timeGridPlugin,
                    interactionPlugin,
                    rrulePlugin,
                ]}
                initialView="dayGridMonth"
                headerToolbar={{
                    left: "prev,next today",
                    center: "title",
                    right: "dayGridMonth,timeGridWeek,timeGridDay",
                }}
                events={events}
                nowIndicator={true}
                editable={true}
                selectable={true}
                selectMirror={true}
                dateClick={handleDateClick}
                eventClick={handleEventClick}
                height="80vh"
                locale={ruLocale}
            />

            {editModalOpen && (
                <div className="modal">
                    <div className="modal-content">
                        {isLoading ? (
                            <div className="loading-message">
                                Загрузка данных...
                            </div>
                        ) : isEventOwner ? (
                            <>
                                <div className="modal-header">
                                    <h2>Просмотр и редактирование события</h2>
                                </div>

                                <div className="modal-body">
                                    <input
                                        type="text"
                                        placeholder="Название"
                                        value={eventData.title || ""}
                                        onChange={(e) =>
                                            setEventData({
                                                ...eventData,
                                                title: e.target.value,
                                            })
                                        }
                                    />

                                    <input
                                        type="text"
                                        placeholder="Описание"
                                        value={eventData.description || ""}
                                        onChange={(e) =>
                                            setEventData({
                                                ...eventData,
                                                description: e.target.value,
                                            })
                                        }
                                    />

                                    <input
                                        type="datetime-local"
                                        value={formatForDateTimeLocal(
                                            eventData.start
                                        )}
                                        onChange={(e) => {
                                            setEventData({
                                                ...eventData,
                                                start: new Date(
                                                    parseDateTimeLocal(
                                                        e.target.value
                                                    )
                                                ),
                                            });
                                        }}
                                    />

                                    <input
                                        type="datetime-local"
                                        value={formatForDateTimeLocal(
                                            eventData.end
                                        )}
                                        onChange={(e) => {
                                            setEventData({
                                                ...eventData,
                                                end: new Date(
                                                    parseDateTimeLocal(
                                                        e.target.value
                                                    )
                                                ),
                                            });
                                        }}
                                    />

                                    <input
                                        type="color"
                                        value={eventData.color}
                                        onChange={(e) =>
                                            setEventData({
                                                ...eventData,
                                                color: e.target.value,
                                            })
                                        }
                                    />

                                    <div className="sharing-section">
                                        <h3>Вы создатель события</h3>
                                    </div>
                                </div>

                                <div className="modal-footer">
                                    <button
                                        onClick={() => setEditModalOpen(false)}
                                    >
                                        Отмена
                                    </button>
                                    <button onClick={handleDeleteEvent}>
                                        Удалить
                                    </button>
                                    <button onClick={handleUpdateEvent}>
                                        Сохранить
                                    </button>
                                </div>
                            </>
                        ) : (
                            <>
                                <div className="modal-header">
                                    <h2>Просмотр события</h2>
                                </div>

                                <div className="modal-body">
                                    <input
                                        type="text"
                                        placeholder="Название"
                                        value={eventData.title || ""}
                                        onChange={(e) =>
                                            setEventData({
                                                ...eventData,
                                                title: e.target.value,
                                            })
                                        }
                                        readOnly
                                    />

                                    <input
                                        type="text"
                                        placeholder="Описание"
                                        value={eventData.description || ""}
                                        onChange={(e) =>
                                            setEventData({
                                                ...eventData,
                                                description: e.target.value,
                                            })
                                        }
                                        readOnly
                                    />

                                    <input
                                        type="datetime-local"
                                        value={formatForDateTimeLocal(
                                            eventData.start
                                        )}
                                        onChange={(e) => {
                                            setEventData({
                                                ...eventData,
                                                start: new Date(
                                                    parseDateTimeLocal(
                                                        e.target.value
                                                    )
                                                ),
                                            });
                                        }}
                                        readOnly
                                    />

                                    <input
                                        type="datetime-local"
                                        value={formatForDateTimeLocal(
                                            eventData.end
                                        )}
                                        onChange={(e) => {
                                            setEventData({
                                                ...eventData,
                                                end: new Date(
                                                    parseDateTimeLocal(
                                                        e.target.value
                                                    )
                                                ),
                                            });
                                        }}
                                        readOnly
                                    />

                                    <input
                                        type="color"
                                        value={eventData.color}
                                        onChange={(e) =>
                                            setEventData({
                                                ...eventData,
                                                color: e.target.value,
                                            })
                                        }
                                        readOnly
                                    />

                                    <div className="sharing-section">
                                        <h3>
                                            Событие предоставлено вам
                                            пользователем:{" "}
                                            <strong>
                                                {owner?.username ||
                                                    "Неизвестный пользователь"}
                                            </strong>
                                        </h3>
                                    </div>
                                </div>

                                <div className="modal-footer-1">
                                    <button
                                        onClick={() => setEditModalOpen(false)}
                                    >
                                        Выйти
                                    </button>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            )}
        </>
    );
};

export default Calendar;

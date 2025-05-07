import ruLocale from "@fullcalendar/core/locales/ru";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import FullCalendar from "@fullcalendar/react";
import rrulePlugin from "@fullcalendar/rrule";
import timeGridPlugin from "@fullcalendar/timegrid";
import React, { useEffect, useState } from "react";
import FriendsService from "../services/FriendsService";
import ScheduleService from "../services/ScheduleService";
import SharedScheduleService from "../services/SharedScheduleService";

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
    const [sharedWithUsers, setSharedWithUsers] = useState([]);
    const [newShareUser, setNewShareUser] = useState("");
    const [friends, setFriends] = useState([]);

    useEffect(() => {
        if (editModalOpen && selectedEvent) {
            const sharedSchedules = SharedScheduleService.getSharedSchedulesWithMe();
            console.log(sharedSchedules);
            
            console.log(sharedSchedules);
            
            console.log(sharedWithUsers);
            

            // Загрузка списка друзей
            FriendsService.getFriends().then(setFriends);
        }
    }, [editModalOpen, selectedEvent]);

    const handleShare = async () => {
        if (!newShareUser) return;

        await SharedScheduleService.createSharedSchedule(
            selectedEvent.id,
            newShareUser,
            "view",
        );

        const updated = await SharedScheduleService.getSharedUsers(
            selectedEvent.id
        );
        setSharedWithUsers(updated);
        setNewShareUser("");
    };

    const handleUnshare = async (userId) => {
        const sharedRecord = sharedWithUsers.find((u) => u.id === userId);
        if (sharedRecord) {
            await SharedScheduleService.unshareSchedule(sharedRecord.shared_id);
            setSharedWithUsers(sharedWithUsers.filter((u) => u.id !== userId));
        }
    };

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
                                value={formatForDateTimeLocal(eventData.start)}
                                onChange={(e) => {
                                    setEventData({
                                        ...eventData,
                                        start: new Date(
                                            parseDateTimeLocal(e.target.value)
                                        ),
                                    });
                                }}
                            />

                            <input
                                type="datetime-local"
                                value={formatForDateTimeLocal(eventData.end)}
                                onChange={(e) => {
                                    setEventData({
                                        ...eventData,
                                        end: new Date(
                                            parseDateTimeLocal(e.target.value)
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
                            <div className="shared-with-section">
                                <h3>Поделено с:</h3>
                                {sharedWithUsers.length > 0 ? (
                                    <ul className="shared-users-list">
                                        {sharedWithUsers.map((user) => (
                                            <li key={user.id}>
                                                {user.username}
                                                <button
                                                    onClick={() =>
                                                        handleUnshare(user.id)
                                                    }
                                                    className="unshare-btn"
                                                >
                                                    Отменить доступ
                                                </button>
                                            </li>
                                        ))}
                                    </ul>
                                ) : (
                                    <p>
                                        Событие не расшарено с другими
                                        пользователями
                                    </p>
                                )}

                                <div className="add-sharing">
                                    <select
                                        value={newShareUser}
                                        onChange={(e) =>
                                            setNewShareUser(e.target.value)
                                        }
                                    >
                                        <option value="">Выберите друга</option>
                                        {friends.map((friend) => (
                                            <option
                                                key={friend.id}
                                                value={friend.id}
                                            >
                                                {friend.username}
                                            </option>
                                        ))}
                                    </select>
                                    <button onClick={handleShare}>
                                        Поделиться
                                    </button>
                                </div>
                            </div>
                        </div>

                        <div className="modal-footer">
                            <button onClick={() => setEditModalOpen(false)}>
                                Отмена
                            </button>
                            <button onClick={handleDeleteEvent}>Удалить</button>
                            <button onClick={handleUpdateEvent}>
                                Сохранить
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default Calendar;

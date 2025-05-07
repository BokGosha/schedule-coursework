import { useEffect, useState } from "react";
import FriendsService from "../services/FriendsService";
import SharedScheduleService from "../services/SharedScheduleService";
import UserService from "../services/UserService";

const EventForm = ({ open, onClose, formData, onChange, onSubmit }) => {
    const {
        title,
        description,
        start_time,
        end_time,
        is_all_day,
        location,
        color,
        is_recurring,
        recurrence_rule,
        category_id,
    } = formData;
    const [friends, setFriends] = useState([]);
    const [selectedFriends, setSelectedFriends] = useState([]);

    useEffect(() => {
        const fetchFriends = async () => {
            try {
                const friendsList = await FriendsService.getFriends("accepted");

                const currentUserId = UserService.getCurrentUser();

                const friendsWithData = await Promise.all(
                    friendsList.map(async (friend) => {
                        const friendId =
                            parseInt(currentUserId) === friend.user_id
                                ? friend.friend_id
                                : friend.user_id;

                        const userData = await UserService.getUserById(
                            friendId
                        );

                        return {
                            ...friends,
                            friendData: userData,
                        };
                    })
                );

                setFriends(friendsWithData);
            } catch (error) {
                console.error("Ошибка загрузки друзей:", error);
            }
        };
        fetchFriends();
    }, []);

    const handleFriendSelect = (friendId) => {
        setSelectedFriends((prev) =>
            prev.includes(friendId)
                ? prev.filter((id) => id !== friendId)
                : [...prev, friendId]
        );
    };

    const handleSubmitWithFriends = async (e) => {
        e.preventDefault();
        const event = await onSubmit();

        if (event && selectedFriends.length > 0) {
            await Promise.all(
                selectedFriends.map((friendId) =>
                    SharedScheduleService.createSharedSchedule(
                        event.id,
                        friendId,
                        "view"
                    )
                )
            );
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

    return (
        open && (
            <div className="modal" style={{ display: "flex" }}>
                <div className="modal-dialog">
                    <div className="modal-content">
                        <div className="modal-header">
                            <h2 className="modal-title">
                                Создать новое событие
                            </h2>
                        </div>
                        <form onSubmit={onSubmit} className="modal-body">
                            <input
                                type="text"
                                name="title"
                                value={title}
                                onChange={(e) =>
                                    onChange(e.target.name, e.target.value)
                                }
                                placeholder="Название*"
                                required
                                className="form-group"
                            />
                            <textarea
                                name="description"
                                value={description}
                                onChange={(e) =>
                                    onChange(e.target.name, e.target.value)
                                }
                                placeholder="Описание"
                                className="form-group"
                            />

                            <input
                                type="datetime-local"
                                name="start_time"
                                value={formatForDateTimeLocal(start_time)}
                                onChange={(e) =>
                                    onChange(
                                        e.target.name,
                                        parseDateTimeLocal(e.target.value)
                                    )
                                }
                                className="form-group"
                            />

                            <input
                                type="datetime-local"
                                name="end_time"
                                value={formatForDateTimeLocal(end_time)}
                                onChange={(e) =>
                                    onChange(
                                        e.target.name,
                                        parseDateTimeLocal(e.target.value)
                                    )
                                }
                                className="form-group"
                            />
                            <label className="form-group">
                                <input
                                    type="checkbox"
                                    name="is_all_day"
                                    checked={is_all_day}
                                    onChange={(e) =>
                                        onChange(
                                            e.target.name,
                                            e.target.checked
                                        )
                                    }
                                />
                                Весь день
                            </label>

                            <input
                                type="text"
                                name="location"
                                value={location}
                                onChange={(e) =>
                                    onChange(e.target.name, e.target.value)
                                }
                                placeholder="Место"
                                className="form-group"
                            />

                            <input
                                type="color"
                                name="color"
                                value={color}
                                onChange={(e) =>
                                    onChange(e.target.name, e.target.value)
                                }
                                className="form-group"
                            />
                            <label className="form-group">
                                <input
                                    type="checkbox"
                                    name="is_recurring"
                                    checked={is_recurring}
                                    onChange={(e) =>
                                        onChange(
                                            e.target.name,
                                            e.target.checked
                                        )
                                    }
                                />
                                Повторяющееся событие
                            </label>

                            {is_recurring && (
                                <div className="form-group">
                                    <select
                                        name="recurrence_rule"
                                        value={recurrence_rule}
                                        onChange={(e) =>
                                            onChange(
                                                e.target.name,
                                                e.target.value
                                            )
                                        }
                                    >
                                        <option value="DAILY">Ежедневно</option>
                                        <option value="WEEKLY">
                                            Еженедельно
                                        </option>
                                        <option value="MONTHLY">
                                            Ежемесячно
                                        </option>
                                        <option value="YEARLY">Ежегодно</option>
                                    </select>
                                </div>
                            )}
                            <div className="form-group">
                                <label>Поделиться с друзьями:</label>
                                <div className="friends-list">
                                    {friends.map((friend) => (
                                        <div
                                            key={friend.friendData.id}
                                            className="friend-item"
                                        >
                                            <input
                                                type="checkbox"
                                                id={`friend-${friend.friendData.id}`}
                                                checked={selectedFriends.includes(
                                                    friend.friendData.id
                                                )}
                                                onChange={() =>
                                                    handleFriendSelect(
                                                        friend.friendData.id
                                                    )
                                                }
                                            />
                                            <label
                                                htmlFor={`friend-${friend.friendData.id}`}
                                            >
                                                {friend.friendData.username}
                                            </label>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="modal-footer">
                                <button onClick={onClose}>Отмена</button>
                                <button
                                    type="submit"
                                    onClick={handleSubmitWithFriends}
                                >
                                    Создать и поделиться
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        )
    );
};

export default EventForm;

import React, { useEffect, useState } from "react";
import UserService from "../services/UserService";

const FriendCard = ({
    friend,
    onAccept,
    onReject,
    onRemove,
    isFriend = false,
}) => {
    const [userData, setUserData] = useState(null);
    const [loading, setLoading] = useState(true);

    const isRequest = parseInt(UserService.getCurrentUser()) === friend.user_id;

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const userIdToFetch = isRequest
                    ? friend.friend_id
                    : friend.user_id;
                const data = await UserService.getUserById(userIdToFetch);
                setUserData(data);
            } catch (error) {
                console.error("Ошибка загрузки данных пользователя:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchUserData();
    }, [friend, isRequest]);

    if (loading) {
        return <div>Загрузка данных пользователя...</div>;
    }

    if (!userData) {
        return <div>Не удалось загрузить данные пользователя</div>;
    }

    return (
        <div className="friend-card">
            <div className="friend-info">
                <h3>{userData.username}</h3>
                <p>{userData.email}</p>
            </div>

            {!isFriend && !isRequest && (
                <div className="friend-actions">
                    <button onClick={() => onAccept(friend.id)}>Принять</button>
                    <button onClick={() => onReject(friend.id)}>
                        Отклонить
                    </button>
                </div>
            )}

            {isFriend && (
                <button onClick={() => onRemove(friend.id)}>Удалить</button>
            )}
        </div>
    );
};

export default FriendCard;

import React, { useState } from "react";
import FriendsService from "../services/FriendsService";

const FriendSearch = ({ onSendRequest }) => {
    const [email, setEmail] = useState("");
    const [user, setUser] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSearch = async () => {
        if (!email) return;

        setLoading(true);
        setError(null);

        try {
            const user = await FriendsService.searchUserByEmail(email);

            setUser(user);
        } catch (error) {
            setError(
                error.response?.data?.detail || "Ошибка поиска пользователя"
            );

            setUser([]);
        } finally {
            setLoading(false);
        }
    };

    const handleSendRequest = async (userId) => {
        try {
            await onSendRequest(userId);
        } catch (error) {
            setError(
                error.response?.data?.detail ||
                    "Ошибка отправления запроса в друзья"
            );
        }
    };

    return (
        <div className="friend-search">
            <h3>Найти друзей по email</h3>

            <div className="search-controls">
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
                <button onClick={handleSearch} disabled={loading}>
                    {loading ? "Поиск..." : "Поиск"}
                </button>
            </div>

            {error && (
                <div className="error">
                    {error.msg || error.message || "Пользователь не найден"}
                </div>
            )}

            {user && (
                <>
                    <div className="user-info">
                        <div>
                            <h4>{user.username}</h4>
                            <p>{user.email}</p>
                        </div>
                    </div>
                    <button onClick={() => handleSendRequest(user.id)}>
                        Добавить
                    </button>
                </>
            )}
        </div>
    );
};

export default FriendSearch;

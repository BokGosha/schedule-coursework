import React, { useEffect, useState } from "react";
import FriendsService from "../services/FriendsService";
import UserService from "../services/UserService";
import FriendCard from "./FriendCard";
import FriendSearch from "./FriendSearch";

const FriendsTabs = () => {
    const [activeTab, setActiveTab] = useState(0);
    const [friends, setFriends] = useState([]);
    const [requests, setRequests] = useState([]);
    const [followers, setFollowers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchFriends = async () => {
        setLoading(true);
        setError(null);

        try {
            const friendsRes = await FriendsService.getFriends("accepted");
            const followersRes = await FriendsService.getFriends("pending");

            const currentUserId = UserService.getCurrentUser();
            const incomingRequests = followersRes.filter(
                (r) => r.friend_id === parseInt(currentUserId)
            );
            const outgoingRequests = followersRes.filter(
                (r) => r.user_id === parseInt(currentUserId)
            );

            setFriends(friendsRes);
            setRequests(outgoingRequests);
            setFollowers(incomingRequests);
        } catch (error) {
            setError(
                error.response?.data?.detail || "Ошибка получения списка друзей"
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchFriends();
    }, []);

    const handleAcceptRequest = async (friendId) => {
        try {
            await FriendsService.respondToFriendRequest(friendId, "accepted");

            fetchFriends();
        } catch (error) {
            setError(
                error.response?.data?.detail || "Ошибка добавления в друзья"
            );
        }
    };

    const handleRejectRequest = async (friendId) => {
        try {
            await FriendsService.removeFriend(friendId);

            fetchFriends();
        } catch (error) {
            setError(
                error.response?.data?.detail ||
                    "Ошибка отмены добавления в друзья"
            );
        }
    };

    const handleRemoveFriend = async (friendId) => {
        try {
            await FriendsService.removeFriend(friendId);

            fetchFriends();
        } catch (error) {
            setError(
                error.response?.data?.detail || "Ошибка удаления из друзей"
            );
        }
    };

    const handleSendRequest = async (userId) => {
        try {
            await FriendsService.sendFriendRequest(userId);

            fetchFriends();
        } catch (error) {
            throw error;
        }
    };

    return (
        <div className="friends-container">
            <FriendSearch onSendRequest={handleSendRequest} />

            {error && <div className="error">{error}</div>}

            <div className="tabs">
                <button onClick={() => setActiveTab(0)}>
                    Друзья ({friends.length})
                </button>
                <button onClick={() => setActiveTab(1)}>
                    Запросы в друзья ({requests.length})
                </button>
                <button onClick={() => setActiveTab(2)}>
                    Подписчики ({followers.length})
                </button>
            </div>

            {loading ? (
                <div>Loading...</div>
            ) : (
                <div className="tab-content">
                    {activeTab === 0 && (
                        <>
                            {friends.length === 0 ? (
                                <p>У вас ещё нет друзей</p>
                            ) : (
                                friends.map((friend) => (
                                    <FriendCard
                                        key={friend.id}
                                        friend={friend}
                                        isFriend={true}
                                        onRemove={handleRemoveFriend}
                                    />
                                ))
                            )}
                        </>
                    )}

                    {activeTab === 1 && (
                        <>
                            {requests.length === 0 ? (
                                <p>У вас нет запросов в друзья</p>
                            ) : (
                                requests.map((request) => (
                                    <FriendCard
                                        key={request.id}
                                        friend={request}
                                        onRemove={handleRemoveFriend}
                                    />
                                ))
                            )}
                        </>
                    )}

                    {activeTab === 2 && (
                        <>
                            {followers.length === 0 ? (
                                <p>Подписчики отсутствуют</p>
                            ) : (
                                followers.map((follower) => (
                                    <FriendCard
                                        key={follower.id}
                                        friend={follower}
                                        onAccept={handleAcceptRequest}
                                        onReject={handleRejectRequest}
                                    />
                                ))
                            )}
                        </>
                    )}
                </div>
            )}
        </div>
    );
};

export default FriendsTabs;

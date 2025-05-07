import axios from "axios";
import AuthService from "./AuthService";

const API_BASE_URL = "/api/v1";

const getFriends = async (status) => {
    let config = {
        method: "GET",
        maxBody: Infinity,
        url: `${API_BASE_URL}/friends/`,
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${AuthService.getToken()}`,
        },
        params: {
            status: status,
        },
    };

    return axios
        .request(config)
        .then((response) => {
            return response.data;
        })
        .catch((error) => {
            throw error;
        });
};

const searchUserByEmail = async (email) => {
    let config = {
        method: "GET",
        maxBody: Infinity,
        url: `${API_BASE_URL}/users/by-email`,
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${AuthService.getToken()}`,
        },
        params: {
            email: email,
        },
    };

    return axios
        .request(config)
        .then((response) => {
            return response.data;
        })
        .catch((error) => {
            throw error;
        });
};

const sendFriendRequest = async (friendId) => {
    let config = {
        method: "POST",
        maxBody: Infinity,
        url: `${API_BASE_URL}/friends/`,
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${AuthService.getToken()}`,
        },
        data: {
            friend_id: friendId,
        },
    };

    return axios
        .request(config)
        .then((response) => {
            return response.data;
        })
        .catch((error) => {
            throw error;
        });
};

const respondToFriendRequest = async (friendId, status) => {
    let config = {
        method: "PUT",
        maxBody: Infinity,
        url: `${API_BASE_URL}/friends/${friendId}`,
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${AuthService.getToken()}`,
        },
        data: {
            status: status,
        },
    };

    return axios
        .request(config)
        .then((response) => {
            return response.data;
        })
        .catch((error) => {
            throw error;
        });
};

const removeFriend = async (friendId) => {
    let config = {
        method: "DELETE",
        maxBody: Infinity,
        url: `${API_BASE_URL}/friends/${friendId}`,
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${AuthService.getToken()}`,
        },
    };

    return axios
        .request(config)
        .then((response) => {
            return response.data;
        })
        .catch((error) => {
            throw error;
        });
};

const FriendsService = {
    getFriends,
    searchUserByEmail,
    sendFriendRequest,
    respondToFriendRequest,
    removeFriend,
};

export default FriendsService;

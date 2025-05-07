import axios from "axios";
import AuthService from "./AuthService";

const API_BASE_URL = "/api/v1";

const getUser = async () => {
    let config = {
        method: "GET",
        maxBody: Infinity,
        url: `${API_BASE_URL}/auth/me`,
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${AuthService.getToken()}`,
        },
    };

    return axios
        .request(config)
        .then((response) => {
            localStorage.setItem("currentUserId", response.data.id);
        })
        .catch((error) => {
            throw error;
        });
};

const getUserById = async (userId) => {
    let config = {
        method: "GET",
        maxBody: Infinity,
        url: `${API_BASE_URL}/users/${userId}`,
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

const getCurrentUser = () => {
    return localStorage.getItem("currentUserId");
};

const logout = () => {
    localStorage.removeItem("currentUserId");
};

const UserService = {
    getUser,
    getCurrentUser,
    getUserById,
    logout,
};

export default UserService;

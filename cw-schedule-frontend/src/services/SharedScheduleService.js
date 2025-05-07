import axios from "axios";
import AuthService from "./AuthService";

const API_BASE_URL = "/api/v1/shared-schedules";

const createSharedSchedule = async (
    scheduleId,
    sharedWithId,
    permissionLevel
) => {
    let config = {
        method: "POST",
        maxBody: Infinity,
        url: `${API_BASE_URL}/`,
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${AuthService.getToken()}`,
        },
        data: {
            schedule_id: scheduleId,
            shared_with_id: sharedWithId,
            permissions_level: permissionLevel,
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

const getSharedUsers = async (scheduleId) => {
    let config = {
        method: "GET",
        maxBody: Infinity,
        url: `${API_BASE_URL}/${scheduleId}`,
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

const getSharedSchedule = async () => {
    let config = {
        method: "GET",
        maxBody: Infinity,
        url: `${API_BASE_URL}/shared-by-me`,
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

const getSharedSchedulesWithMe = async () => {
    let config = {
        method: "GET",
        maxBody: Infinity,
        url: `${API_BASE_URL}/shared-with-me`,
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

const getSharedSchedulesWithMeWithData = async () => {
    let config = {
        method: "GET",
        maxBody: Infinity,
        url: `${API_BASE_URL}/shared-with-me-with-data`,
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

const SharedScheduleService = {
    createSharedSchedule,
    getSharedUsers,
    getSharedSchedule,
    getSharedSchedulesWithMe,
    getSharedSchedulesWithMeWithData,
};

export default SharedScheduleService;

import axios from "axios";
import AuthService from "./AuthService";

const API_BASE_URL = "/api/v1/schedules";

const getSchedules = async (startDate, endDate) => {
    const params = {};

    let config = {
        method: "GET",
        maxBody: Infinity,
        url: `${API_BASE_URL}/`,
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${AuthService.getToken()}`,
        },
        params: {
            if(startDate) {
                params.start_date = startDate.toISOString();
            },
            if(endDate) {
                params.end_date = endDate.toISOString();
            },
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

const getScheduleById = async (scheduleId) => {
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

const createSchedule = async (scheduleData) => {
    let config = {
        method: "POST",
        maxBody: Infinity,
        url: `${API_BASE_URL}/`,
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${AuthService.getToken()}`,
        },
        data: {
            title: scheduleData.title,
            start_time: scheduleData.start_time,
            end_time: scheduleData.end_time,
            ...(scheduleData.description && {
                description: scheduleData.description,
            }),
            ...(scheduleData.is_all_day !== undefined && {
                is_all_day: scheduleData.is_all_day,
            }),
            ...(scheduleData.location && { location: scheduleData.location }),
            ...(scheduleData.color && { color: scheduleData.color }),
            ...(scheduleData.is_recurring !== undefined && {
                is_recurring: scheduleData.is_recurring,
            }),
            ...(scheduleData.recurrence_rule && {
                recurrence_rule: scheduleData.recurrence_rule,
            }),
            ...(scheduleData.category_id && {
                category_id: scheduleData.category_id,
            }),
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

const updateSchedule = async (scheduleId, scheduleData) => {
    let config = {
        method: "PUT",
        maxBody: Infinity,
        url: `${API_BASE_URL}/${scheduleId}`,
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${AuthService.getToken()}`,
        },
        data: {
            title: scheduleData.title,
            start_time: scheduleData.start_time,
            end_time: scheduleData.end_time,
            ...(scheduleData.description && {
                description: scheduleData.description,
            }),
            ...(scheduleData.color && { color: scheduleData.color }),
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

const deleteSchedule = async (scheduleId) => {
    let config = {
        method: "DELETE",
        maxBody: Infinity,
        url: `${API_BASE_URL}/${scheduleId}`,
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${AuthService.getToken()}`,
        },
    };

    return axios
        .request(config)
        .then(() => {
            return true;
        })
        .catch((error) => {
            throw error;
        });
};

const ScheduleService = {
    getSchedules,
    createSchedule,
    updateSchedule,
    deleteSchedule,
    getScheduleById,
};

export default ScheduleService;

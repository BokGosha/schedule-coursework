import axios from "axios";

const API_BASE_URL = "/api/v1";

const register = async (email, username, password) => {
    let config = {
        method: "POST",
        maxBody: Infinity,
        url: `${API_BASE_URL}/users/`,
        headers: {
            "Content-Type": "application/json",
        },
        data: {
            email: email,
            username: username,
            password: password,
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

const login = async (email, password) => {
    const config = {
        method: "POST",
        url: `${API_BASE_URL}/auth/login`,
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data: {
            username: email,
            password: password,
        },
    };

    return axios
        .request(config)
        .then((response) => {
            localStorage.setItem("token", response.data.access_token);

            return true;
        })
        .catch((error) => {
            localStorage.removeItem("token");

            throw error;
        });
};

const logout = () => {
    localStorage.removeItem("token");
};

const getToken = () => {
    return localStorage.getItem("token");
};

const AuthService = {
    register,
    login,
    logout,
    getToken,
};

export default AuthService;

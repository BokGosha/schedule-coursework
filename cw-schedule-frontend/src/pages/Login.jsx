import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context";
import AuthService from "../services/AuthService";
import UserService from "../services/UserService";

const Login = () => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const { setIsAuth } = useContext(AuthContext);
    const router = useNavigate();

    const login = async (e) => {
        e.preventDefault();

        try {
            const response = await AuthService.login(email, password);

            if (response) {
                setIsAuth(true);

                await UserService.getUser();

                router("/schedules");
            } else {
                setIsAuth(false);
            }
        } catch (error) {
            alert(
                error.response?.data?.detail ||
                    "Ошибка регистрации пользователя"
            );
        }
    };

    return (
        <div className="auth-form">
            <h1>Авторизация</h1>

            <form onSubmit={login}>
                <input
                    type="email"
                    placeholder="email@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />

                <input
                    type="password"
                    placeholder="Пароль"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />

                <button type="submit">Войти</button>

                <button
                    type="button"
                    className="register-btn"
                    onClick={() => router("/auth/register")}
                >
                    Перейти к регистрации
                </button>
            </form>
        </div>
    );
};

export default Login;

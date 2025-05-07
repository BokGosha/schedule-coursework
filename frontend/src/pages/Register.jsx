import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import AuthService from "../services/AuthService";

const Register = () => {
    const [email, setEmail] = useState("");
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [passwordConfirm, setPasswordConfirm] = useState("");
    const router = useNavigate();

    const register = async (e) => {
        e.preventDefault();

        if (password !== passwordConfirm) {
            alert("Введенные пароли не совпадают!");

            setPasswordConfirm("");

            return;
        }

        try {
            const response = await AuthService.register(
                email,
                username,
                password
            );

            if (response) {
                router("/auth/login");
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
            <h1>Регистрация</h1>

            <form onSubmit={register}>
                <input
                    type="email"
                    placeholder={"email@example.com"}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />

                <input
                    type="username"
                    placeholder={"username"}
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />

                <input
                    type="password"
                    placeholder={"Пароль"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />

                <input
                    type="password"
                    placeholder={"Подтверждение пароля"}
                    value={passwordConfirm}
                    onChange={(e) => setPasswordConfirm(e.target.value)}
                />

                <button type={"submit"}>Зарегистрироваться</button>
            </form>
        </div>
    );
};

export default Register;

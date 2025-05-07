import React, { useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "../context";
import AuthService from "../services/AuthService";
import UserService from "../services/UserService";

const Header = () => {
    const { isAuth, setIsAuth } = useContext(AuthContext);
    const router = useNavigate();

    const logout = () => {
        AuthService.logout();

        UserService.logout();

        localStorage.removeItem("selectedColor");

        setIsAuth(false);
    };

    const login = () => {
        router("/auth/login");
    };

    return (
        <div className="header-container">
            <h1 className="header-h1">Schedule</h1>

            <div className="header-div">
                {isAuth ? (
                    <>
                        <Link to="./schedules" className="header-a">
                            Расписание
                        </Link>
                        <Link to="./friends" className="header-a">
                            Друзья
                        </Link>
                        <button onClick={logout} className="header-button">
                            Выйти
                        </button>
                    </>
                ) : (
                    <button onClick={login} className="header-button">
                        Войти
                    </button>
                )}
            </div>
        </div>
    );
};

export default Header;

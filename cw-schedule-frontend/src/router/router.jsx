import Friends from "../pages/Friends";
import Home from "../pages/Home";
import Login from "../pages/Login";
import Register from "../pages/Register";
import Schedule from "../pages/Schedule";

export const privateRoutes = [
    { path: "/friends", element: Friends },
    { path: "/home", element: Home },
    { path: "/schedules", element: Schedule },
];

export const publicRoutes = [
    { path: "/home", element: Home },
    { path: "/auth/login", element: Login },
    { path: "/auth/register", element: Register },
];

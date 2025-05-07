import Friends from "../pages/Friends";
import Login from "../pages/Login";
import Register from "../pages/Register";
import Schedule from "../pages/Schedule";

export const privateRoutes = [
    { path: "/friends", element: Friends },
    { path: "/schedules", element: Schedule },
];

export const publicRoutes = [
    { path: "/auth/login", element: Login },
    { path: "/auth/register", element: Register },
];

import { Route, Routes } from "react-router-dom";

import Layout from "./components/Layout.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import Catalog from "./pages/Catalog.jsx";
import Certificates from "./pages/Certificates.jsx";
import CourseDetail from "./pages/CourseDetail.jsx";
import ConfirmToken from "./pages/ConfirmToken.jsx";
import CourseEditor from "./pages/CourseEditor.jsx";
import ForgotPassword from "./pages/ForgotPassword.jsx";
import Home from "./pages/Home.jsx";
import LessonPage from "./pages/LessonPage.jsx";
import Login from "./pages/Login.jsx";
import MyCourses from "./pages/MyCourses.jsx";
import NotFound from "./pages/NotFound.jsx";
import Profile from "./pages/Profile.jsx";
import Register from "./pages/Register.jsx";
import ResetPassword from "./pages/ResetPassword.jsx";
import TeacherDashboard from "./pages/TeacherDashboard.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        {/* Открытые страницы */}
        <Route path="/" element={<Home />} />
        <Route path="/catalog" element={<Catalog />} />
        <Route path="/courses/:id" element={<CourseDetail />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password/:token" element={<ResetPassword />} />
        {/* Ссылки из писем: открываются в любом браузере, вход не требуется */}
        <Route path="/verify-email/:token" element={<ConfirmToken mode="verify" />} />
        <Route path="/change-email/:token" element={<ConfirmToken mode="change" />} />

        {/* Требуют входа */}
        <Route element={<ProtectedRoute />}>
          <Route path="/my-courses" element={<MyCourses />} />
          <Route path="/lessons/:id" element={<LessonPage />} />
          <Route path="/certificates" element={<Certificates />} />
          <Route path="/profile" element={<Profile />} />
        </Route>

        {/* Только для преподавателей */}
        <Route element={<ProtectedRoute teacherOnly />}>
          <Route path="/teach" element={<TeacherDashboard />} />
          <Route path="/teach/courses/new" element={<CourseEditor />} />
          <Route path="/teach/courses/:id" element={<CourseEditor />} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}

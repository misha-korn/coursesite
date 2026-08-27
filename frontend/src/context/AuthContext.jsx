import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { api, tokens } from "../api/client.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // При старте приложения проверяем, живой ли сохранённый токен.
  useEffect(() => {
    let cancelled = false;

    async function loadUser() {
      if (!tokens.access) {
        setLoading(false);
        return;
      }
      try {
        const me = await api.get("/api/me/");
        if (!cancelled) setUser(me);
      } catch {
        tokens.clear();
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadUser();
    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (username, password) => {
    const data = await api.post("/api/auth/login/", { username, password });
    tokens.save(data.access, data.refresh);
    const me = await api.get("/api/me/");
    setUser(me);
    return me;
  }, []);

  const register = useCallback(
    async (payload) => {
      await api.post("/api/auth/register/", payload);
      return login(payload.username, payload.password);
    },
    [login]
  );

  const logout = useCallback(() => {
    tokens.clear();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      login,
      register,
      logout,
      isTeacher: user?.role === "teacher",
    }),
    [user, loading, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth можно вызывать только внутри AuthProvider");
  return ctx;
}

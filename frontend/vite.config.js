import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// Прокси намеренно НЕ используется.
// Фронтенд живёт на localhost:5173, а API на localhost:8000. Для браузера это
// разные origin, поэтому запросы к API становятся кросс-доменными, и сервер
// обязан явно разрешить их заголовками CORS. Как это настроить - см. README.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // Явно указываем IPv4-адрес. Без этого Node резолвит имя "localhost"
    // по порядку, заданному ОС: на Windows это часто IPv6 (::1), а браузер
    // при этом идёт на IPv4 (127.0.0.1), и соединение не устанавливается.
    host: "127.0.0.1",
    port: 5173,
  },
});

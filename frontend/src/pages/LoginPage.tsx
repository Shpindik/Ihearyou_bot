import DarkModeIcon from "@mui/icons-material/DarkMode";
import LightModeIcon from "@mui/icons-material/LightMode";
import TelegramIcon from "@mui/icons-material/Telegram";
import {
  Box,
  Button,
  Container,
  IconButton,
  Paper,
  Stack,
  TextField,
  Typography,
  useTheme,
} from "@mui/material";
import { useState } from "react";

import { useAuth } from "../context/AuthContext";
import { useColorMode } from "../theme";

export function LoginPage() {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const theme = useTheme();
  const { toggleMode, mode } = useColorMode();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(username, password);
    } catch (err) {
      console.error(err);
      setError("Неверный логин или пароль");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ minHeight: "100vh" }}>
      <Stack
        justifyContent="center"
        alignItems="center"
        sx={{
          minHeight: "100vh",
          transition: theme.transitions.create("background-color", {
            duration: theme.transitions.duration.shorter,
          }),
        }}
      >
        <Paper elevation={0} sx={{ p: 6, width: "100%", borderRadius: 5 }}>
          <Stack spacing={4} alignItems="center">
            <Box
              sx={{
                width: 96,
                height: 96,
                borderRadius: "50%",
                background: "linear-gradient(135deg, #2AABEE, #229ED9)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "white",
              }}
            >
              <TelegramIcon sx={{ fontSize: 48 }} />
            </Box>
            <Box textAlign="center">
              <Typography variant="h5" fontWeight={600} gutterBottom>
                Вход в админку
              </Typography>
              <Typography color="text.secondary">
                Используйте учетные данные администратора
              </Typography>
            </Box>
            <IconButton
              aria-label="Переключить тему"
              onClick={toggleMode}
              color="primary"
            >
              {mode === "dark" ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>
            <Box component="form" onSubmit={handleSubmit} sx={{ width: "100%" }}>
              <Stack spacing={2.5}>
                <TextField
                  label="Логин"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  fullWidth
                  autoComplete="username"
                />
                <TextField
                  label="Пароль"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  fullWidth
                  autoComplete="current-password"
                />
                {error && (
                  <Typography color="error" textAlign="center">
                    {error}
                  </Typography>
                )}
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={loading}
                >
                  {loading ? "Входим..." : "Войти"}
                </Button>
              </Stack>
            </Box>
          </Stack>
        </Paper>
      </Stack>
    </Container>
  );
}

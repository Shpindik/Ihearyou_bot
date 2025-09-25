import DarkModeIcon from "@mui/icons-material/DarkMode";
import LightModeIcon from "@mui/icons-material/LightMode";
import LogoutIcon from "@mui/icons-material/Logout";
import TelegramIcon from "@mui/icons-material/Telegram";
import {
  AppBar,
  Avatar,
  Box,
  Container,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Paper,
  Stack,
  Toolbar,
  Typography,
} from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { useEffect, useState } from "react";

import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { useColorMode } from "../theme";

type User = {
  id: number;
  user_id: number;
  username?: string | null;
  fullname?: string | null;
  avatar_url?: string | null;
};

export function DashboardPage() {
  const { logout } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const theme = useTheme();
  const { toggleMode, mode } = useColorMode();

  const loadUsers = async () => {
    setLoading(true);
    try {
      const response = await api.get<User[]>("/users");
      setUsers(response.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadUsers();
  }, []);

  return (
    <Box
      sx={{
        backgroundColor: theme.palette.background.default,
        minHeight: "100vh",
        transition: theme.transitions.create("background-color", {
          duration: theme.transitions.duration.shorter,
        }),
      }}
    >
      <AppBar position="static" color="primary" enableColorOnDark sx={{ boxShadow: "none" }}>
        <Toolbar>
          <Avatar sx={{ bgcolor: "transparent", mr: 2 }}>
            <TelegramIcon />
          </Avatar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            IHearYou Admin
          </Typography>
          <IconButton
            color="inherit"
            onClick={toggleMode}
            aria-label="Переключить тему"
            sx={{ mr: 1 }}
          >
            {mode === "dark" ? <LightModeIcon /> : <DarkModeIcon />}
          </IconButton>
          <IconButton color="inherit" onClick={logout}>
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ py: 6 }}>
        <Paper sx={{ p: 4, borderRadius: 5 }} elevation={mode === "dark" ? 3 : 1}>
          <Stack spacing={3}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="h5" fontWeight={600}>
                Пользователи
              </Typography>
            </Box>

            <Paper
              variant="outlined"
              sx={{
                borderRadius: 4,
                overflow: "hidden",
                backgroundColor: theme.palette.background.paper,
                borderColor: theme.palette.divider,
              }}
            >
              <List disablePadding>
                {users.length === 0 && !loading && (
                  <ListItem>
                    <ListItemText
                      primary="Нет пользователей"
                      secondary="Список пока пуст"
                    />
                  </ListItem>
                )}
                {users.map((item, index) => (
                  <Box key={item.id}>
                    <ListItem alignItems="flex-start">
                      <ListItemAvatar>
                        {item.avatar_url ? (
                          <Avatar src={item.avatar_url} alt={item.username || String(item.user_id)} />
                        ) : (
                          <Avatar sx={{ background: "linear-gradient(135deg, #2AABEE, #229ED9)" }}>
                            <TelegramIcon />
                          </Avatar>
                        )}
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Stack direction="row" spacing={2} alignItems="center">
                            <Typography variant="subtitle1" fontWeight={600}>
                              {item.username ? `@${item.username}` : `Пользователь #${item.user_id}`}
                            </Typography>
                          </Stack>
                        }
                        secondary={
                          <>
                            {item.fullname && (
                              <Typography component="span" color="text.primary">
                                {item.fullname}
                              </Typography>
                            )}
                          </>
                        }
                        secondaryTypographyProps={{ mt: 1 }}
                      />
                    </ListItem>
                    {index < users.length - 1 && <Divider component="li" variant="inset" />}
                  </Box>
                ))}
              </List>
            </Paper>
          </Stack>
        </Paper>
      </Container>
    </Box>
  );
}

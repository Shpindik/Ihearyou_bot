import { PaletteMode } from "@mui/material";
import { createTheme, ThemeOptions } from "@mui/material/styles";
import {
  createContext,
  PropsWithChildren,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

const baseOptions: ThemeOptions = {
  typography: {
    fontFamily: "'Roboto', 'Helvetica', 'Arial', sans-serif",
    button: {
      textTransform: "none",
      fontWeight: 600,
      borderRadius: 16,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          padding: "10px 24px",
          boxShadow: "none",
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 24,
        },
      },
    },
  },
};

const paletteByMode: Record<PaletteMode, ThemeOptions["palette"]> = {
  light: {
    mode: "light",
    primary: {
      main: "#24A1DE",
    },
    background: {
      default: "#F5F8FB",
      paper: "#FFFFFF",
    },
    text: {
      primary: "#0B1929",
      secondary: "#334155",
    },
  },
  dark: {
    mode: "dark",
    primary: {
      main: "#24A1DE",
    },
    background: {
      default: "#0F172A",
      paper: "#1E293B",
    },
    text: {
      primary: "#F8FAFC",
      secondary: "#CBD5F5",
    },
  },
};

export const createAppTheme = (mode: PaletteMode) =>
  createTheme({
    ...baseOptions,
    palette: paletteByMode[mode],
  });

type ColorModeContextValue = {
  mode: PaletteMode;
  theme: ReturnType<typeof createAppTheme>;
  toggleMode: () => void;
};

const ColorModeContext = createContext<ColorModeContextValue | undefined>(
  undefined
);

const STORAGE_KEY = "app-color-mode";

const getSystemPreference = (): PaletteMode =>
  window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";

const getInitialMode = (): PaletteMode => {
  if (typeof window === "undefined") {
    return "light";
  }

  const stored = window.localStorage.getItem(STORAGE_KEY) as PaletteMode | null;
  if (stored === "light" || stored === "dark") {
    return stored;
  }

  return getSystemPreference();
};

export const ColorModeProvider = ({ children }: PropsWithChildren) => {
  const [mode, setMode] = useState<PaletteMode>(() => getInitialMode());

  useEffect(() => {
    const handler = (event: MediaQueryListEvent) => {
      setMode(event.matches ? "dark" : "light");
    };

    const media = window.matchMedia("(prefers-color-scheme: dark)");
    media.addEventListener("change", handler);

    return () => media.removeEventListener("change", handler);
  }, []);

  const theme = useMemo(() => createAppTheme(mode), [mode]);

  const toggleMode = useCallback(() => {
    setMode((prev) => {
      const next = prev === "light" ? "dark" : "light";
      window.localStorage.setItem(STORAGE_KEY, next);
      return next;
    });
  }, []);

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, mode);
  }, [mode]);

  const value = useMemo(
    () => ({
      mode,
      theme,
      toggleMode,
    }),
    [mode, theme, toggleMode]
  );

  return (
    <ColorModeContext.Provider value={value}>{children}</ColorModeContext.Provider>
  );
};

export const useColorMode = () => {
  const context = useContext(ColorModeContext);
  if (!context) {
    throw new Error("useColorMode must be used within ColorModeProvider");
  }
  return context;
};

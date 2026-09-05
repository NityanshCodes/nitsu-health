import { createContext, type ReactNode } from "react";

interface ThemeContextValue {
  mode: "light";
}

export const ThemeContext = createContext<ThemeContextValue | null>(null);

export const ThemeProvider = ({ children }: { children: ReactNode }) => {
  return (
    <ThemeContext.Provider value={{ mode: "light" }}>
      {children}
    </ThemeContext.Provider>
  );
};

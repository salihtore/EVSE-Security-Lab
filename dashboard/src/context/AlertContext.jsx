import { createContext, useContext, useState } from "react";

const AlertContext = createContext(null);

export function AlertProvider({ children }) {
  const [selectedAlert, setSelectedAlert] = useState(null);

  return (
    <AlertContext.Provider value={{ selectedAlert, setSelectedAlert }}>
      {children}
    </AlertContext.Provider>
  );
}

export function useAlert() {
  const ctx = useContext(AlertContext);
  if (!ctx) {
    throw new Error("useAlert must be used inside AlertProvider");
  }
  return ctx;
}

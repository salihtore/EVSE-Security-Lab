// useCpStream.js
import { useEffect, useState } from "react";

export default function useCpStream() {
  const [cps, setCps] = useState([]);

  useEffect(() => {
    const source = new EventSource("http://localhost:8000/cp/live");

    source.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setCps(data); // backend array gönderiyor varsayımı
      } catch {}
    };

    return () => source.close();
  }, []);

  return cps;
}

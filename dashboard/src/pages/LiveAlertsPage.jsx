import React from "react";
// DÜZELTME: Süslü parantez { } eklendi.
import { useSecurityStream } from "../hooks/useSecurityStream";
import AlarmCard from "../components/AlarmCard";

export default function LiveAlerts() {
  const { alerts, connected } = useSecurityStream();

  return (
    <aside style={{ 
      width: '100%', 
      maxWidth: 350, // Biraz daha geniş alan
      background: '#111', 
      border: '1px solid #333',
      borderRadius: '8px',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      maxHeight: '600px', // Sonsuza kadar uzamaması için sınır
      color: '#e0e0e0'
    }}>
      
      {/* Header Kısmı */}
      <div style={{ 
        padding: '12px 15px', 
        borderBottom: '1px solid #333',
        background: '#161625',
        borderTopLeftRadius: '8px',
        borderTopRightRadius: '8px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: '600' }}>
          🚨 Live Stream
        </h3>
        
        {/* Bağlantı Durumu Göstergesi */}
        <span style={{ 
          fontSize: '0.75rem', 
          fontWeight: 'bold',
          color: connected ? '#00C851' : '#ff4444',
          background: connected ? 'rgba(0, 200, 81, 0.1)' : 'rgba(255, 68, 68, 0.1)',
          padding: '2px 8px',
          borderRadius: '4px'
        }}>
          {connected ? "● LIVE" : "○ OFFLINE"}
        </span>
      </div>

      {/* Kaydırılabilir Liste Alanı */}
      <div style={{ 
        padding: '12px', 
        overflowY: 'auto', // Çok alarm gelirse kaydırma çubuğu çıksın
        flex: 1 
      }}>
        {alerts.length === 0 && (
          <div style={{ textAlign: 'center', padding: '20px', color: '#666' }}>
            <p>No active threats detected.</p>
          </div>
        )}

        {alerts.map((alert, index) => (
          // ÖNEMLİ: Hook kodunda 'event_id' kullandığın için key olarak onu verdik.
          // Yoksa index kullanılır.
          <AlarmCard key={alert.event_id || index} alert={alert} />
        ))}
      </div>
    </aside>
  );
}
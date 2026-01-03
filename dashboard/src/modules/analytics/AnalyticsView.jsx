import React from 'react';
import { useEventStore } from '../../store/eventStore';

export const AnalyticsView = () => {
  const events = useEventStore((state) => state.events);

  // Basit İstatistik Hesaplama
  const total = events.length;
  
  // Saldırı Tiplerini Sayalım
  const stats = events.reduce((acc, curr) => {
    const type = curr.event_type || curr.anomaly_type || curr.ocpp_type || 'Diğer';
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {});

  // En çok tekrarlanan ilk 3 olayı bul
  const topEvents = Object.entries(stats)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3);

  return (
    <div style={{ display: 'flex', gap: '20px', marginTop: '20px', marginBottom: '20px' }}>
      
      {/* 1. KART: Toplam Olay Sayacı */}
      <div style={{ 
        flex: 1, 
        background: 'linear-gradient(145deg, #1e1e2f, #252535)', 
        padding: '20px', 
        borderRadius: '12px', 
        border: '1px solid #444',
        boxShadow: '0 4px 15px rgba(0,0,0,0.3)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <div style={{ fontSize: '30px' }}>📊</div>
          <div>
            <h4 style={{ margin: 0, color: '#aaa', fontSize: '12px', textTransform: 'uppercase' }}>Toplam Aktivite</h4>
            <p style={{ fontSize: '32px', fontWeight: 'bold', margin: '5px 0', color: '#fff', textShadow: '0 0 10px rgba(255,255,255,0.3)' }}>
              {total}
            </p>
          </div>
        </div>
      </div>

      {/* 2. KART: Canlı Saldırı Analizi (YENİ!) */}
      <div style={{ 
        flex: 2, // Bu kart daha geniş olsun
        background: '#1e1e2f', 
        padding: '15px 25px', 
        borderRadius: '12px', 
        border: '1px solid #444',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center'
      }}>
        <h4 style={{ margin: '0 0 10px 0', color: '#00d2ff', fontSize: '12px', textTransform: 'uppercase' }}>⚡ Anlık Olay Dağılımı</h4>
        
        {/* Barlar */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {topEvents.length === 0 ? (
            <span style={{ color: '#555', fontStyle: 'italic' }}>Veri bekleniyor...</span>
          ) : (
            topEvents.map(([type, count], i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ color: '#ccc', fontSize: '12px', width: '80px' }}>{type}</span>
                {/* İlerleme Çubuğu Arka Planı */}
                <div style={{ flex: 1, height: '8px', background: '#333', borderRadius: '4px', overflow: 'hidden' }}>
                  {/* Doluluk Oranı */}
                  <div style={{ 
                    width: `${(count / total) * 100}%`, 
                    height: '100%', 
                    background: i === 0 ? '#ff4444' : (i === 1 ? '#ffbb33' : '#00C851'),
                    borderRadius: '4px',
                    transition: 'width 0.5s ease'
                  }}></div>
                </div>
                <span style={{ color: '#fff', fontSize: '12px', minWidth: '30px', textAlign: 'right' }}>{count}</span>
              </div>
            ))
          )}
        </div>
      </div>

      {/* 3. KART: Sistem Durumu */}
      <div style={{ 
        flex: 1, 
        background: '#1e1e2f', 
        padding: '20px', 
        borderRadius: '12px', 
        border: '1px solid #444',
        textAlign: 'center',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
         <div style={{ 
           width: '15px', height: '15px', 
           borderRadius: '50%', 
           background: '#0f0', 
           boxShadow: '0 0 15px #0f0',
           marginBottom: '10px'
         }}></div>
         <p style={{ margin: 0, color: '#fff', fontWeight: 'bold' }}>SYSTEM ONLINE</p>
         <small style={{ color: '#666' }}>Port: 8000</small>
      </div>

    </div>
  );
};
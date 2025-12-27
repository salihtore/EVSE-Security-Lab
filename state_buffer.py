import time
from collections import deque

class StateBuffer:
    """
    Sadece kısa süreli state tutmak için (window mantığı).
    ML ve feature extractor bu state'i güvenle kullanabilir.
    """
    def __init__(self, window_seconds=10):
        self.window_seconds = window_seconds
        # cp_id -> {
        #   'last_event_ts': float,
        #   'event_timestamps': deque([ts, ts, ...]),
        #   'session_active': bool,
        #   'last_meter_value': float,
        #   'meter_history': deque([(ts, val), ...]),
        #   'plugged': bool
        # }
        self.buffers = {}

    def update(self, event):
        """
        Her event geldiğinde çağrılır. State'i günceller.
        Asla exception atmaz.
        """
        try:
            if not isinstance(event, dict):
                return

            cp_id = event.get('cp_id')
            if not cp_id:
                return

            # Timestamp processing
            ts = event.get('timestamp')
            if ts is None:
                ts = time.time()
            else:
                try:
                    ts = float(ts)
                except (ValueError, TypeError):
                    ts = time.time()

            # Initialize buffer for cp_id if needed
            if cp_id not in self.buffers:
                self.buffers[cp_id] = {
                    'last_event_ts': 0.0,
                    'event_timestamps': deque(),
                    'session_active': False,
                    'last_meter_value': 0.0,
                    'meter_history': deque(),
                    'plugged': False
                }
            
            buf = self.buffers[cp_id]
            current_time = time.time()  # Use system time for window cleanup reference, or event ts? 
                                        # Usually event ts is better if we are processing historical data, 
                                        # but "window mantığı" usually implies 'now'. 
                                        # Prompt says "timestamp yoksa time.time() kullan".
                                        # I will use 'ts' for logical consistency with the event stream.

            # 1. Update last_event_ts
            if ts > buf['last_event_ts']:
                buf['last_event_ts'] = ts

            # 2. Update event_timestamps (deque)
            buf['event_timestamps'].append(ts)
            # Cleanup old events outside window relative to current event ts
            while buf['event_timestamps'] and (ts - buf['event_timestamps'][0] > self.window_seconds):
                buf['event_timestamps'].popleft()

            # 3. Update session_active
            action = event.get('action', '')
            if action == 'StartTransaction':
                buf['session_active'] = True
            elif action == 'StopTransaction':
                buf['session_active'] = False
            
            # Also check if explicit 'session_active' field exists
            if 'session_active' in event:
                buf['session_active'] = bool(event['session_active'])

            # 4. Update meter values
            # Assumes 'meter_value' key might exist
            val = event.get('meter_value')
            if val is not None:
                try:
                    val_float = float(val)
                    buf['last_meter_value'] = val_float
                    buf['meter_history'].append((ts, val_float))
                    # Cleanup old meter values
                    while buf['meter_history'] and (ts - buf['meter_history'][0][0] > self.window_seconds):
                        buf['meter_history'].popleft()
                except (ValueError, TypeError):
                    pass

            # 5. Update plugged status
            if 'plugged' in event:
                buf['plugged'] = bool(event['plugged'])
            # Infer from status if possible
            status = event.get('status')
            if status == 'Occupied':
                buf['plugged'] = True
            elif status == 'Available':
                buf['plugged'] = False

        except Exception:
            # Asla exception atma
            pass

    def snapshot(self, cp_id):
        """
        Features for ML.
        Eksik veri varsa 0 veya False dön.
        """
        try:
            if cp_id not in self.buffers:
                return {
                    'events_last_10s': 0,
                    'time_since_last_event': 0.0,
                    'session_active': False,
                    'meter_delta_10s': 0.0,
                    'plugged': False
                }

            buf = self.buffers[cp_id]
            now = time.time() 
            # Note: snapshot is typically asked "now". 
            # If we are in simulation, we might need a reference time passed in.
            # But prompt says "time_since_last_event". I will use time.time() vs last_event_ts.

            # Cleanup specifically for the snapshot "view" if needed, 
            # strictly speaking 'events_last_10s' should be relative to 'now'.
            # The update method cleans relative to 'latest event', which might be old.
            # I will filter the existing deque relative to 'now'.
            
            # 1. events_last_10s
            # Count events in [now - window, now]
            events_count = 0
            for t in buf['event_timestamps']:
                if now - t <= self.window_seconds:
                    events_count += 1
            
            # 2. time_since_last_event
            time_since = 0.0
            if buf['last_event_ts'] > 0:
                diff = now - buf['last_event_ts']
                time_since = max(0.0, diff)

            # 3. session_active
            s_active = buf['session_active']

            # 4. meter_delta_10s
            # Difference between last known meter value and the one ~10s ago (or oldest in window)
            m_delta = 0.0
            if buf['meter_history']:
                current_val = buf['meter_history'][-1][1]
                # Find oldest value within window relative to 'now' (or just oldest in history if valid)
                # Ideally we want value closest to (now - 10s).
                # Since we only keep history for window_seconds in update, the [0] element is the oldest.
                # But we should check if it's too old (unlikely given update logic) or too recent.
                
                # Simple logic: last - first in window
                first_val = buf['meter_history'][0][1]
                m_delta = current_val - first_val

            # 5. plugged
            is_plugged = buf['plugged']

            return {
                'events_last_10s': events_count,
                'time_since_last_event': time_since,
                'session_active': s_active,
                'meter_delta_10s': m_delta,
                'plugged': is_plugged
            }

        except Exception:
            return {
                'events_last_10s': 0,
                'time_since_last_event': 0.0,
                'session_active': False,
                'meter_delta_10s': 0.0,
                'plugged': False
            }

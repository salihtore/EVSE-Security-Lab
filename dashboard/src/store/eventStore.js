// Dosya: src/store/eventStore.js
import { create } from 'zustand';

export const useEventStore = create((set) => ({
  events: [],
  // Yeni gelen olayı listenin en başına ekler
  addEvent: (newEvent) => set((state) => ({ 
    events: [newEvent, ...state.events] 
  })),
}));
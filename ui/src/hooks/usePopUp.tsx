import { useState, useCallback } from 'react';
import { type PopUpItem } from '../components/shared/PopUp';

export function usePopUp() {
  const [queue, setQueue] = useState<PopUpItem[]>([]);

  const addPopUp = useCallback((popUp: Omit<PopUpItem, 'id'>) => {
    const id = crypto.randomUUID();
    setQueue(prev => [...prev, { ...popUp, id }]);
  }, []);

  const removePopUp = useCallback(() => {
    setQueue(prev => prev.slice(1));
  }, []);

  return {
    popUps: queue.slice(0, 1),
    addPopUp,
    removePopUp,
  };
}
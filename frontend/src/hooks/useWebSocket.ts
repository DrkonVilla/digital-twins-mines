import { useEffect, useRef } from 'react';
import { useAuthStore } from '@/store/authStore';

export const useWebSocket = (url: string, onMessage: (data: any) => void) => {
  const ws = useRef<WebSocket | null>(null);
  const token = useAuthStore((state) => state.token);

  useEffect(() => {
    if (!token) return;

    // Connect to WebSocket with token
    const wsUrl = `${url}?token=${token}`;
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log('WebSocket Connected');
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (e) {
        console.error('Error parsing WS message', e);
      }
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket Error', error);
    };

    ws.current.onclose = () => {
      console.log('WebSocket Disconnected');
    };

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [url, token, onMessage]);

  return ws.current;
};

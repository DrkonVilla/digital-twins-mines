import { useEffect, useRef, useCallback } from 'react';

export const useWebSocket = (url: string, onMessage: (data: any) => void) => {
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  const connect = useCallback(() => {
    if (!mountedRef.current) return;

    try {
      ws.current = new WebSocket(url);

      ws.current.onopen = () => {
        console.log('[WS] Connected:', url);
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (e) {
          console.warn('[WS] Could not parse message:', event.data);
        }
      };

      ws.current.onerror = () => {
        // onerror fires before onclose — just log quietly, reconnect in onclose
        console.warn('[WS] Connection error, will attempt reconnect...');
      };

      ws.current.onclose = (event) => {
        console.log(`[WS] Disconnected (code: ${event.code}). Reconnecting in 5s...`);
        if (mountedRef.current) {
          reconnectTimer.current = setTimeout(connect, 5000);
        }
      };
    } catch (err) {
      console.warn('[WS] Failed to create WebSocket connection:', err);
      if (mountedRef.current) {
        reconnectTimer.current = setTimeout(connect, 5000);
      }
    }
  }, [url, onMessage]);

  useEffect(() => {
    mountedRef.current = true;
    connect();

    return () => {
      mountedRef.current = false;
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      if (ws.current) {
        ws.current.onclose = null; // Prevent reconnect on intentional unmount
        ws.current.close();
      }
    };
  }, [connect]);

  return ws;
};

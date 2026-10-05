type MessageCallback = (data: any) => void;

export class ProjectWebSocket {
  private ws: WebSocket | null = null;
  private projectId: string;
  private listeners: Map<string, Set<MessageCallback>> = new Map();
  private reconnectTimeout: any = null;
  private pingInterval: any = null;
  private isExplicitlyClosed = false;

  constructor(projectId: string) {
    this.projectId = projectId;
  }

  public connect() {
    this.isExplicitlyClosed = false;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/projects/${this.projectId}`;

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log(`[WebSocket] Connected to project ${this.projectId}`);
      // Start ping heartbeat
      this.pingInterval = setInterval(() => {
        if (this.ws?.readyState === WebSocket.OPEN) {
          this.ws.send('ping');
        }
      }, 25000);
    };

    this.ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        const eventType = payload.event;
        const data = payload.data;

        // Notify specific event listeners
        if (this.listeners.has(eventType)) {
          this.listeners.get(eventType)?.forEach((cb) => cb(data));
        }

        // Notify wildcard listener
        if (this.listeners.has('*')) {
          this.listeners.get('*')?.forEach((cb) => cb(payload));
        }
      } catch (err) {
        // Ping response or raw text
      }
    };

    this.ws.onclose = () => {
      clearInterval(this.pingInterval);
      if (!this.isExplicitlyClosed) {
        this.reconnectTimeout = setTimeout(() => this.connect(), 2000);
      }
    };

    this.ws.onerror = (err) => {
      console.warn('[WebSocket] Error:', err);
    };
  }

  public on(event: string, callback: MessageCallback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)?.add(callback);
    return () => {
      this.listeners.get(event)?.delete(callback);
    };
  }

  public disconnect() {
    this.isExplicitlyClosed = true;
    clearInterval(this.pingInterval);
    clearTimeout(this.reconnectTimeout);
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.listeners.clear();
  }
}

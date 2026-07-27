export const DEFAULT_SIEVE_WIDTH_CM = 1.5;
export const DEFAULT_SIEVE_HEIGHT_CM = 3.0;

export const CONNECTION_STATUS = {
    CONNECTING: "connecting",
    CONNECTED: "connected",
    DISCONNECTED: "disconnected",
};

export const STREAM_STATUS = {
    STARTING: "starting",
    ACTIVE: "active",
    DOWN: "down",
};

export const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws";
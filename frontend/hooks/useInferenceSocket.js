"use client";

import { useEffect, useMemo, useState } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { CONNECTION_STATUS, STREAM_STATUS, WS_URL } from "@/lib/constants";

let idCounter = 0;
function nextMaskId() {
    idCounter += 1;
    return `mask-${Date.now()}-${idCounter}`;
}

const READY_STATE_TO_CONNECTION = {
    [ReadyState.CONNECTING]: CONNECTION_STATUS.CONNECTING,
    [ReadyState.OPEN]: CONNECTION_STATUS.CONNECTED,
};

/**
 * Subscribes to the backend's /ws inference stream and exposes the latest
 * frame, its masks, and the connection/stream status as plain state.
 *
 * IMPORTANT — conformity semantics (per the mesh / lost-product pivot):
 * `mask.conformity === true` means the particle is SMALLER than the sieve
 * opening in both dimensions — i.e. a small particle STUCK on the mesh
 * that should have fallen through. That's the problem case the whole
 * system exists to catch, so it's the one flagged/highlighted (accent
 * green) in the UI — the opposite of what "conformity" sounds like it
 * should mean at a glance. `conformity === false` is a normal,
 * appropriately-sized particle — nothing to flag.
 *
 * `flaggedMasks` below filters on `mask.conformity` (not `!mask.conformity`)
 * for exactly this reason.
 */
export function useInferenceSocket() {
    const [imageData, setImageData] = useState(null);
    const [masksData, setMasksData] = useState([]);
    const [lastResultDate, setLastResultDate] = useState(null);
    const [conformityPercentage, setConformityPercentage] = useState(null); // sourced from data.stuck_percentage
    const [error, setError] = useState(null);
    const [streamStatus, setStreamStatus] = useState(STREAM_STATUS.STARTING);

    const { lastMessage, readyState, getWebSocket } = useWebSocket(WS_URL, {
        shouldReconnect: () => true,
        reconnectAttempts: 10,
        reconnectInterval: 3000,
        onOpen: () => setError(null),
        onError: () => setError("Connection error. Please check if the server is running."),
    });

    useEffect(() => {
        if (!lastMessage) return;

        try {
            const data = JSON.parse(lastMessage.data);

            if (data.status === STREAM_STATUS.DOWN) {
                setStreamStatus(STREAM_STATUS.DOWN);
                return;
            }
            if (data.status === STREAM_STATUS.STARTING) {
                setStreamStatus(STREAM_STATUS.STARTING);
                return;
            }
            if (data.status === STREAM_STATUS.ACTIVE) {
                setStreamStatus(STREAM_STATUS.ACTIVE);
            }

            if (data.image) setImageData(data.image);

            if (Array.isArray(data.masks_data)) {
                setMasksData(data.masks_data.map((mask) => ({ ...mask, id: nextMaskId() })));
                setLastResultDate(new Date());
            }

            // Backend field may be named `stuck_percentage` (per the pivot) or
            // still `non_conformity_percentage` (older naming) — accept either
            // so this doesn't silently break if the rename hasn't actually
            // landed on the running backend. Numerically it's the same "%
            // flagged" quantity StatsRow's "Non-conformité" card expects.
            const percentage = data.stuck_percentage ?? data.non_conformity_percentage;
            if (percentage !== undefined) {
                setConformityPercentage(percentage);
            }
        } catch (parseError) {
            console.error("Error parsing WebSocket message:", parseError);
            setError("Error processing data from server");
        }
    }, [lastMessage]);

    const connectionStatus = READY_STATE_TO_CONNECTION[readyState] ?? CONNECTION_STATUS.DISCONNECTED;

    // The flagged/stuck particles — see the semantics note above.
    const flaggedMasks = useMemo(() => masksData.filter((mask) => !mask.conformity), [masksData])

    const reconnect = () => {
        getWebSocket()?.close();
    };

    return {
        imageData,
        masksData,
        flaggedMasks,
        lastResultDate,
        conformityPercentage,
        error,
        streamStatus,
        connectionStatus,
        reconnect,
    };
}
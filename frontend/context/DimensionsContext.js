"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { fetchSieveDimensions, saveSieveDimensions } from "@/lib/api";
import { DEFAULT_SIEVE_WIDTH_CM, DEFAULT_SIEVE_HEIGHT_CM } from "@/lib/constants";

const DimensionsContext = createContext(null);

export function DimensionsProvider({ children }) {
    const [dimensions, setDimensions] = useState({
        width: DEFAULT_SIEVE_WIDTH_CM,
        height: DEFAULT_SIEVE_HEIGHT_CM,
    });
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        let cancelled = false;

        async function loadDimensions() {
            try {
                setIsLoading(true);
                setError(null);
                const data = await fetchSieveDimensions();
                if (cancelled) return;
                setDimensions({
                    width: data.width_cm ?? DEFAULT_SIEVE_WIDTH_CM,
                    height: data.height_cm ?? DEFAULT_SIEVE_HEIGHT_CM,
                });
            } catch (err) {
                if (!cancelled) {
                    console.error("Error fetching dimensions:", err);
                    setError("Impossible de récupérer les dimensions depuis le serveur.");
                }
            } finally {
                if (!cancelled) setIsLoading(false);
            }
        }

        loadDimensions();
        return () => {
            cancelled = true;
        };
    }, []);

    const updateDimensions = useCallback(async (newWidth, newHeight) => {
        const updated = await saveSieveDimensions(newWidth, newHeight);
        setDimensions({
            width: updated.width_cm ?? newWidth,
            height: updated.height_cm ?? newHeight,
        });
        return updated;
    }, []);

    return (
        <DimensionsContext.Provider value={{ ...dimensions, isLoading, error, updateDimensions }}>
            {children}
        </DimensionsContext.Provider>
    );
}

export function useDimensions() {
    const context = useContext(DimensionsContext);
    if (!context) {
        throw new Error("useDimensions must be used within a DimensionsProvider");
    }
    return context;
}
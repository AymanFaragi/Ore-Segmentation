"use client";

import { Loader2, VideoOff, WifiOff } from "lucide-react";

const VARIANTS = {
    disconnected: {
        icon: WifiOff,
        title: "Problème de connexion au serveur",
        message: "Vérifiez que le serveur est démarré, puis réessayez la connexion.",
    },
    down: {
        icon: VideoOff,
        title: "Source vidéo indisponible",
        message: "La caméra ne renvoie aucune image pour le moment.",
    },
    starting: {
        icon: Loader2,
        title: "Initialisation du flux…",
        message: "En attente de la première image de la caméra.",
        spin: true,
    },
};

export default function StreamStatusView({ variant, onRetry }) {
    const config = VARIANTS[variant];
    if (!config) return null;
    const Icon = config.icon;

    return (
        <div
            role="status"
            aria-live="polite"
            className="flex h-[360px] flex-col items-center justify-center gap-4 rounded-panel panel-surface px-6 text-center lg:h-[700px]"
        >
            <Icon
                size={48}
                strokeWidth={1.5}
                aria-hidden="true"
                className={config.spin ? "animate-spin text-accent" : "text-text-muted"}
            />
            <div className="flex flex-col gap-1">
                <p className="text-lg font-medium text-text-title">{config.title}</p>
                <p className="max-w-sm text-sm text-text-muted">{config.message}</p>
            </div>
            {variant === "disconnected" && onRetry && (
                <button
                    type="button"
                    onClick={onRetry}
                    className="mt-2 inline-flex items-center gap-2 rounded-pill bg-gradient-to-r from-accent-soft to-accent px-6 py-2.5 text-sm font-semibold text-bg-to shadow-glow"
                >
                    Réessayer la connexion
                </button>
            )}
        </div>
    );
}
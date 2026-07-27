import { Loader2 } from "lucide-react";

export default function LoadingState({ message = "Chargement en cours…" }) {
    return (
        <div
            role="status"
            aria-live="polite"
            className="flex min-h-[40vh] flex-col items-center justify-center gap-3 text-text-muted"
        >
            <Loader2 size={32} className="animate-spin text-accent" aria-hidden="true" />
            <p className="text-sm">{message}</p>
        </div>
    );
}
function capitalize(text) {
    return text.charAt(0).toUpperCase() + text.slice(1);
}

function formatDetectionDate(date) {
    if (!date) return "Analyse en pause";
    const formatted = date.toLocaleDateString("fr-FR", {
        day: "numeric",
        month: "long",
        year: "numeric",
    });
    return capitalize(formatted);
}

export default function DetectionDateHeading({ date }) {
    return (
        <div className="flex flex-wrap items-baseline gap-8 text-2xl font-medium text-text-heading lg:text-[30px]">
            <span>Date de Détection :</span>
            <span>{formatDetectionDate(date)}</span>
        </div>
    );
}
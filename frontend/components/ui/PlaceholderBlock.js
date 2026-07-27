export default function PlaceholderBlock({ label, className = "" }) {
    return (
        <div
            role="status"
            className={`flex items-center justify-center rounded-panel border border-dashed border-text-muted/30 bg-panel-from/20 p-4 text-center text-sm text-text-muted ${className}`}
        >
            {label}
        </div>
    );
}
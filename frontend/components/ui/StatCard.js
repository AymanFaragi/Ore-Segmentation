export default function StatCard({ label, value, valueSuffix, glow = "single" }) {
    const shadowClass =
        glow === "double"
            ? "[text-shadow:0_0_4px_rgba(208,208,208,0.25),0_0_4px_rgba(192,255,137,0.25)]"
            : "[text-shadow:0_0_4px_rgba(192,255,137,0.25)]";

    return (
        <div className="flex h-auto min-h-[165px] w-full flex-col gap-3 rounded-card panel-surface px-[15px] pt-[15px] lg:h-[145px] lg:w-[264px]">
            <p className="text-xl font-medium text-text-heading lg:text-[23px]">{label}</p>
            <p className={`text-4xl font-medium text-text-stat lg:text-[55px] ${shadowClass}`}>
                {value}
                {valueSuffix && <span className="text-accent">{valueSuffix}</span>}
            </p>
        </div>
    );
}
import StatCard from "../ui/StatCard";

export default function StatsRow({ conformityPercentage, totalMasks, nonConformCount }) {
    const conformingCount = totalMasks != null && nonConformCount != null ? totalMasks - nonConformCount : null;

    return (
        <div className="flex flex-wrap gap-4">
            <StatCard
                label="Non-conformité"
                value={conformityPercentage ?? "—"}
                valueSuffix={conformityPercentage != null ? "%" : null}
                glow="double"
            />
            <StatCard label="Particules détectées" value={totalMasks ?? "—"} />
            <StatCard label="Particules conformes" value={conformingCount ?? "—"} />
        </div>
    );
}
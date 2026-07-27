// Temporary mock dataset shared by StatsRow and the charts during UI-only
// development. All three consume the SAME array so the numbers stay
// consistent with each other (e.g. StatsRow's "100 détectées / 23%
// non-conformes" matches what the charts actually plot). Deleted once real
// masksData arrives via useInferenceSocket() in the backend-wiring step.

function seededRandom(seed) {
    let value = seed;
    return () => {
        value = (value * 9301 + 49297) % 233280;
        return value / 233280;
    };
}

export function generateMockMasksData(total = 100, nonConformRatio = 0.23) {
    const random = seededRandom(42);

    return Array.from({ length: total }, (_, index) => {
        const minDim = Number((0.5 + random() * 6.5).toFixed(2));
        const maxDim = Number((minDim + random() * 2.5).toFixed(2));
        const conformity = random() >= nonConformRatio;
        return { id: `mock-${index}`, minDim, maxDim, conformity };
    });
}
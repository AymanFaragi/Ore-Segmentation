export default function GlowDot({
                                    cx,
                                    cy,
                                    color,
                                    radius = 4,
                                    haloRadius = 8,
                                    haloOpacity = 0.25,
                                    onMouseEnter,
                                    onMouseLeave,
                                }) {
    const interactive = Boolean(onMouseEnter || onMouseLeave);

    return (
        <g style={interactive ? { cursor: "pointer" } : undefined}>
            <circle cx={cx} cy={cy} r={haloRadius} fill={color} opacity={haloOpacity} />
            <circle cx={cx} cy={cy} r={radius} fill={color} stroke="#FFFFFF" strokeWidth={1} />
            {interactive && (
                <circle
                    cx={cx}
                    cy={cy}
                    r={Math.max(haloRadius, 10)}
                    fill="transparent"
                    onMouseEnter={onMouseEnter}
                    onMouseLeave={onMouseLeave}
                />
            )}
        </g>
    );
}
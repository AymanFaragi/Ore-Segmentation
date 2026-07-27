"use client";

import { ParentSize } from "@visx/responsive";
import { scaleLinear } from "@visx/scale";
import { LinePath } from "@visx/shape";
import { curveCatmullRom } from "@visx/curve";
import { GridRows, GridColumns } from "@visx/grid";
import { AxisBottom, AxisLeft } from "@visx/axis";
import { useTooltip, TooltipWithBounds } from "@visx/tooltip";
import ChartCard from "./ChartCard";
import ChartLegend from "./ChartLegend";
import GlowDot from "./GlowDot";
import { buildDensityCurve } from "@/lib/kde";

const TITLE = "Répartition des tailles des roches (densité)";
const MARGIN = { top: 16, right: 20, bottom: 36, left: 40 };
const TICK_LABEL_PROPS = {
    fill: "var(--color-text-muted)",
    fontSize: 13,
};
const LEGEND_ITEMS = [
    { label: "Dimension min", color: "#BABABA" },
    { label: "Dimension max", color: "#C0FF89" },
];

function DensityChartInner({ width, height, data }) {
    const { tooltipData, tooltipLeft, tooltipTop, tooltipOpen, showTooltip, hideTooltip } = useTooltip();

    const innerWidth = width - MARGIN.left - MARGIN.right;
    const innerHeight = height - MARGIN.top - MARGIN.bottom;

    const minValues = data.map((d) => d.min_dim);
    const maxValues = data.map((d) => d.max_dim);
    const domain = [Math.min(...minValues, ...maxValues), Math.max(...minValues, ...maxValues)];

    const { path: minPath, markers: minMarkers } = buildDensityCurve(minValues, domain);
    const { path: maxPath, markers: maxMarkers } = buildDensityCurve(maxValues, domain);

    const yMax = Math.max(...minPath.map((p) => p.y), ...maxPath.map((p) => p.y), 0.01);

    const xScale = scaleLinear({ domain, range: [0, innerWidth] });
    const yScale = scaleLinear({ domain: [0, yMax * 1.15], range: [innerHeight, 0] });

    const handlePointHover = (point, series) => () =>
        showTooltip({
            tooltipData: { ...point, series },
            tooltipLeft: MARGIN.left + xScale(point.x),
            tooltipTop: MARGIN.top + yScale(point.y) - 10,
        });

    return (
        <div className="relative">
            <svg width={width} height={height} role="img" aria-label={TITLE}>
                <g transform={`translate(${MARGIN.left},${MARGIN.top})`}>
                    <GridRows
                        scale={yScale}
                        width={innerWidth}
                        stroke="var(--color-grid-dashed)"
                        strokeDasharray="4 4"
                        numTicks={4}
                    />
                    <GridColumns
                        scale={xScale}
                        height={innerHeight}
                        stroke="var(--color-grid-dashed)"
                        strokeDasharray="4 4"
                        numTicks={7}
                    />

                    <LinePath
                        data={minPath}
                        x={(d) => xScale(d.x)}
                        y={(d) => yScale(d.y)}
                        curve={curveCatmullRom}
                        stroke="#BABABA"
                        strokeWidth={1.5}
                    />
                    <LinePath
                        data={maxPath}
                        x={(d) => xScale(d.x)}
                        y={(d) => yScale(d.y)}
                        curve={curveCatmullRom}
                        stroke="#C0FF89"
                        strokeWidth={1.5}
                    />

                    {minMarkers.map((point, i) => (
                        <GlowDot
                            key={`min-${i}`}
                            cx={xScale(point.x)}
                            cy={yScale(point.y)}
                            color="#BABABA"
                            onMouseEnter={handlePointHover(point, "min")}
                            onMouseLeave={hideTooltip}
                        />
                    ))}
                    {maxMarkers.map((point, i) => (
                        <GlowDot
                            key={`max-${i}`}
                            cx={xScale(point.x)}
                            cy={yScale(point.y)}
                            color="#C0FF89"
                            onMouseEnter={handlePointHover(point, "max")}
                            onMouseLeave={hideTooltip}
                        />
                    ))}

                    <AxisBottom
                        top={innerHeight}
                        scale={xScale}
                        numTicks={7}
                        stroke="var(--color-grid-solid)"
                        tickStroke="var(--color-grid-solid)"
                        tickLabelProps={() => ({ ...TICK_LABEL_PROPS, textAnchor: "middle", dy: 4 })}
                    />
                    <AxisLeft
                        scale={yScale}
                        numTicks={4}
                        stroke="transparent"
                        tickStroke="transparent"
                        tickFormat={(v) => v.toFixed(1)}
                        tickLabelProps={() => ({ ...TICK_LABEL_PROPS, textAnchor: "end", dx: -8, dy: 4 })}
                    />
                </g>
            </svg>

            {tooltipOpen && tooltipData && (
                <TooltipWithBounds
                    left={tooltipLeft}
                    top={tooltipTop}
                    className="pointer-events-none rounded-md border border-white/10 panel-surface px-3 py-2 text-xs text-text-body shadow-card"
                >
                    <p
                        className="mb-1 font-semibold"
                        style={{ color: tooltipData.series === "min" ? "#BABABA" : "#C0FF89" }}
                    >
                        {tooltipData.series === "min" ? "Dimension min" : "Dimension max"}
                    </p>
                    <p>Diamètre : {tooltipData.x.toFixed(2)} cm</p>
                    <p>Densité : {tooltipData.y.toFixed(3)}</p>
                </TooltipWithBounds>
            )}
        </div>
    );
}

export default function DensityChart({ data }) {
    if (!data || data.length < 2) {
        return (
            <ChartCard title={TITLE}>
                <p className="py-10 text-center text-sm text-text-muted">
                    Pas assez de données pour générer le graphique.
                </p>
            </ChartCard>
        );
    }

    return (
        <ChartCard title={TITLE}>
            <div className="flex items-stretch gap-1">
                <div className="flex w-4 shrink-0 items-center justify-center">
                    <span className="-rotate-90 whitespace-nowrap text-sm text-text-muted">Density</span>
                </div>
                <div className="min-w-0 flex-1">
                    <div className="h-[260px] w-full">
                        <ParentSize>
                            {({ width, height }) =>
                                width > 0 && height > 0 && <DensityChartInner width={width} height={height} data={data} />
                            }
                        </ParentSize>
                    </div>
                    <p className="mt-1 text-center text-sm text-text-muted">Diameter (cm)</p>
                </div>
            </div>
            <ChartLegend items={LEGEND_ITEMS} />
        </ChartCard>
    );
}
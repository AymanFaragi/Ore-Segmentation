"use client";

import { ParentSize } from "@visx/responsive";
import { scaleLinear } from "@visx/scale";
import { GridRows, GridColumns } from "@visx/grid";
import { AxisBottom, AxisLeft } from "@visx/axis";
import { useTooltip, TooltipWithBounds } from "@visx/tooltip";
import ChartCard from "./ChartCard";
import ChartLegend from "./ChartLegend";
import GlowDot from "./GlowDot";

const TITLE = "Roches Conformes vs Non Conformes";
const MARGIN = { top: 16, right: 20, bottom: 36, left: 40 };
const TICK_LABEL_PROPS = {
    fill: "var(--color-text-muted)",
    fontSize: 13,
};
const LEGEND_ITEMS = [
    { label: "Conforme", color: "#C0FF89" },
    { label: "Non conforme", color: "#D8D8D8" },
];

function ScatterChartInner({ width, height, data }) {
    const { tooltipData, tooltipLeft, tooltipTop, tooltipOpen, showTooltip, hideTooltip } = useTooltip();

    const innerWidth = width - MARGIN.left - MARGIN.right;
    const innerHeight = height - MARGIN.top - MARGIN.bottom;

    const minValues = data.map((d) => d.min_dim);
    const maxValues = data.map((d) => d.max_dim);

    const xScale = scaleLinear({
        domain: [Math.min(...minValues), Math.max(...minValues)],
        range: [0, innerWidth],
        nice: true,
    });
    const yScale = scaleLinear({
        domain: [Math.min(...maxValues), Math.max(...maxValues)],
        range: [innerHeight, 0],
        nice: true,
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

                    {data.map((point) => (
                        <GlowDot
                            key={point.id}
                            cx={xScale(point.min_dim)}
                            cy={yScale(point.max_dim)}
                            color={point.conformity ? "#C0FF89" : "#D8D8D8"}
                            haloOpacity={point.conformity ? 0.35 : 0.15}
                            radius={4}
                            haloRadius={6}
                            onMouseEnter={() =>
                                showTooltip({
                                    tooltipData: point,
                                    tooltipLeft: MARGIN.left + xScale(point.min_dim),
                                    tooltipTop: MARGIN.top + yScale(point.max_dim) - 10,
                                })
                            }
                            onMouseLeave={hideTooltip}
                        />
                    ))}

                    <AxisBottom
                        top={innerHeight}
                        scale={xScale}
                        numTicks={7}
                        stroke="var(--color-grid-solid)"
                        tickStroke="var(--color-grid-solid)"
                        tickFormat={(v) => Math.round(v)}
                        tickLabelProps={() => ({ ...TICK_LABEL_PROPS, textAnchor: "middle", dy: 4 })}
                    />
                    <AxisLeft
                        scale={yScale}
                        numTicks={4}
                        stroke="transparent"
                        tickStroke="transparent"
                        tickFormat={(v) => Math.round(v)}
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
                        style={{ color: tooltipData.conformity ? "#C0FF89" : "#D8D8D8" }}
                    >
                        {tooltipData.conformity ? "Conforme" : "Non conforme"}
                    </p>
                    <p>Dimension min : {tooltipData.min_dim} cm</p>
                    <p>Dimension max : {tooltipData.max_dim} cm</p>
                </TooltipWithBounds>
            )}
        </div>
    );
}

export default function ConformityScatterChart({ data }) {
    if (!data || data.length === 0) {
        return (
            <ChartCard title={TITLE}>
                <p className="py-10 text-center text-sm text-text-muted">Aucune donnée disponible.</p>
            </ChartCard>
        );
    }

    return (
        <ChartCard title={TITLE}>
            <div className="flex items-stretch gap-1">
                <div className="flex w-4 shrink-0 items-center justify-center">
                    <span className="-rotate-90 whitespace-nowrap text-sm text-text-muted">Max Dimension</span>
                </div>
                <div className="min-w-0 flex-1">
                    <div className="h-[260px] w-full">
                        <ParentSize>
                            {({ width, height }) =>
                                width > 0 && height > 0 && <ScatterChartInner width={width} height={height} data={data} />
                            }
                        </ParentSize>
                    </div>
                    <p className="mt-1 text-center text-sm text-text-muted">Min Dimension</p>
                </div>
            </div>
            <ChartLegend items={LEGEND_ITEMS} />
        </ChartCard>
    );
}
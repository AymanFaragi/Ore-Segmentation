"use client";

import { useEffect, useState } from "react";
import DashboardGrid from "./DashboardGrid";
import DetectionDateHeading from "./DetectionDateHeading";
import StatsRow from "./StatsRow";
import SieveDimensionsPanel from "./SieveDimensionsPanel";
import MaskGallery from "./MaskGallery";
import LiveFeedSection from "./LiveFeedSection";
import DensityChart from "../charts/DensityChart";
import ConformityScatterChart from "../charts/ConformityScatterChart";
import LoadingState from "../ui/LoadingState";
import { useDimensions } from "@/context/DimensionsContext";
import { useInferenceSocket } from "@/hooks/useInferenceSocket";

export default function Dashboard() {
    const { width, height, updateDimensions, isLoading, error: dimensionsError } = useDimensions();
    const {
        imageData,
        masksData,
        flaggedMasks,
        lastResultDate,
        conformityPercentage,
        streamStatus,
        connectionStatus,
        reconnect,
    } = useInferenceSocket();

    const [selectedIds, setSelectedIds] = useState([]);

    useEffect(() => {
        setSelectedIds([]);
    }, [lastResultDate]);

    const toggleMask = (id) => {
        setSelectedIds((previous) =>
            previous.includes(id) ? previous.filter((existing) => existing !== id) : [...previous, id]
        );
    };

    const totalMasks = masksData.length;
    const nonConformCount = flaggedMasks.length;

    const roches = flaggedMasks.map((mask, index) => ({
        ...mask,
        label: `Roche ${index + 1}`,
        selected: selectedIds.includes(mask.id),
    }));

    const overlays = roches.filter((mask) => mask.selected);

    if (isLoading) {
        return <LoadingState message="Chargement des dimensions de la maille…" />;
    }

    return (
        <DashboardGrid
            topBar={
                <div className="flex flex-col gap-3">
                    <DetectionDateHeading date={lastResultDate} />
                    <div className="flex flex-wrap gap-5">
                        <StatsRow
                            conformityPercentage={conformityPercentage}
                            totalMasks={totalMasks}
                            nonConformCount={nonConformCount}
                        />
                        <div className="flex flex-1 flex-col gap-2">
                            <SieveDimensionsPanel width={width} height={height} onUpdate={updateDimensions} />
                            {dimensionsError && <p className="text-sm text-red-400">{dimensionsError}</p>}
                        </div>
                    </div>
                </div>
            }
            feed={
                <LiveFeedSection
                    connectionStatus={connectionStatus}
                    streamStatus={streamStatus}
                    imageData={imageData}
                    overlays={overlays}
                    onRetry={reconnect}
                />
            }
            charts={[
                <DensityChart key="density" data={masksData} />,
                <ConformityScatterChart key="scatter" data={masksData} />,
            ]}
            sidebar={<MaskGallery masks={roches} onToggle={toggleMask} />}
        />
    );
}
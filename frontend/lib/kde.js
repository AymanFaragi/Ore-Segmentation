import { kernelDensityEstimation } from "simple-statistics";

/**
 * Builds a smooth density curve (many finely-stepped points, for the SVG
 * path) plus a fixed number of evenly spaced marker points along the same
 * domain. The Figma design places ~10 evenly-spaced glowing dots per line
 * regardless of how many raw values exist underneath — so markers are
 * sampled independently from the path resolution, not one-per-datum.
 */
export function buildDensityCurve(values, domain, { steps = 80, markerCount = 10 } = {}) {
    if (!values || values.length < 2) return { path: [], markers: [] };

    const kde = kernelDensityEstimation(values);
    const [min, max] = domain;
    const step = (max - min) / steps;

    const path = [];
    for (let i = 0; i <= steps; i += 1) {
        const x = min + i * step;
        path.push({ x, y: kde(x) });
    }

    const markerStep = (max - min) / (markerCount - 1);
    const markers = [];
    for (let i = 0; i < markerCount; i += 1) {
        const x = min + i * markerStep;
        markers.push({ x, y: kde(x) });
    }

    return { path, markers };
}
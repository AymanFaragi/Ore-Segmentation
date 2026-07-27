"use client";

import { DimensionsProvider } from "@/context/DimensionsContext";

export default function Providers({ children }) {
    return <DimensionsProvider>{children}</DimensionsProvider>;
}
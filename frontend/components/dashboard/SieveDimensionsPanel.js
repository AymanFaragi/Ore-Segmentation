"use client";

import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import NumericStepperField from "../ui/NumericStepperField";

export default function SieveDimensionsPanel({ width, height, onUpdate }) {
    const [sieveWidth, setSieveWidth] = useState(width);
    const [sieveHeight, setSieveHeight] = useState(height);
    const [isSaving, setIsSaving] = useState(false);
    const [feedback, setFeedback] = useState(null);

    useEffect(() => setSieveWidth(width), [width]);
    useEffect(() => setSieveHeight(height), [height]);

    const isUnchanged = sieveWidth === width && sieveHeight === height;
    const isDisabled = isSaving || sieveWidth == null || sieveHeight == null || isUnchanged;

    const handleSave = async () => {
        try {
            setIsSaving(true);
            setFeedback(null);
            await onUpdate(sieveWidth, sieveHeight);
            setFeedback({ type: "success", message: "Dimensions mises à jour avec succès." });
        } catch (error) {
            setFeedback({
                type: "error",
                message: `Erreur lors de la mise à jour des dimensions : ${error.message}`,
            });
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <section
            aria-label="Dimensions de la maille"
            className="flex w-full flex-col gap-5 rounded-card panel-surface px-[27px] pt-5 pb-6 lg:w-[672px] lg:flex-none"
        >
            <div className="flex justify-between">
                <h2 className="text-xl font-medium text-text-heading lg:text-[23px]">
                    Dimensions des mailles
                </h2>
                <button
                    type="button"
                    onClick={handleSave}
                    disabled={isDisabled}
                    className="inline-flex items-center gap-2 rounded-[15px] bg-gradient-to-r from-accent-soft to-accent px-6 py-2.5 text-sm font-semibold text-bg-to shadow-glow transition-opacity disabled:opacity-40 disabled:shadow-none"
                >
                    {isSaving && <Loader2 size={16} className="animate-spin" aria-hidden="true" />}
                    Actualiser
                </button>
            </div>


            <div className="flex flex-wrap items-end gap-8">
                <NumericStepperField
                    id="sieve-width"
                    label="Largeur de la maille (cm)"
                    value={sieveWidth}
                    onChange={setSieveWidth}
                />
                <NumericStepperField
                    id="sieve-height"
                    label="Longueur de la maille (cm)"
                    value={sieveHeight}
                    onChange={setSieveHeight}
                />


            </div>
        </section>
    );
}
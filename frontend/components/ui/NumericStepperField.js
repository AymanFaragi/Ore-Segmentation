"use client";

import { ChevronDown, ChevronUp } from "lucide-react";

/**
 * Matches the Figma "0.0" input widgets: a small rounded-10px field with
 * two tiny chevron buttons stacked on the right instead of native browser
 * number-input spinners (which are hidden via appearance-none).
 *
 * Purely a local-state control — saving/committing is handled by the
 * parent's explicit "Actualiser" button, not here.
 */
export default function NumericStepperField({
                                                id,
                                                label,
                                                value,
                                                onChange,
                                                step = 0.1,
                                                min = 0.1,
                                            }) {
    const clamp = (n) => Math.max(min, Math.round(n * 10) / 10);

    const handleStep = (direction) => {
        onChange(clamp((value ?? 0) + direction * step));
    };

    return (
        <label htmlFor={id} className="flex w-[285px] max-w-full flex-col gap-2">
            <span className="text-sm font-normal text-text-title">{label}</span>
            <span className="relative flex items-center rounded-input bg-field">
        <input
            id={id}
            type="number"
            inputMode="decimal"
            step={step}
            min={min}
            value={value ?? ""}
            onChange={(event) => onChange(Number(event.target.value))}
            onBlur={(event) => onChange(clamp(Number(event.target.value)))}
            className="w-full appearance-none bg-transparent py-2 pl-3 pr-8 text-sm font-medium text-text-faint outline-none [-moz-appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
        />
        <span className="absolute right-2 flex flex-col">
          <button
              type="button"
              onClick={() => handleStep(1)}
              aria-label={`Augmenter : ${label}`}
              className="flex h-3 items-center justify-center text-text-faint/70 hover:text-accent"
          >
            <ChevronUp size={13} strokeWidth={2.5} aria-hidden="true" />
          </button>
          <button
              type="button"
              onClick={() => handleStep(-1)}
              aria-label={`Diminuer : ${label}`}
              className="flex h-3 items-center justify-center text-text-faint/70 hover:text-accent"
          >
            <ChevronDown size={13} strokeWidth={2.5} aria-hidden="true" />
          </button>
        </span>
      </span>
        </label>
    );
}
"use client";

export default function MaskGallery({ masks, onToggle }) {
    return (
        <section
            aria-label="Roches non conformes détectées"
            className="flex h-full flex-col gap-5 rounded-xl panel-surface shadow-panel overflow-y-auto px-[26px] pt-8 pb-8"
        >
            <h2 className="text-2xl font-normal text-text-heading lg:text-[27px]">Roches</h2>

            {masks.length === 0 ? (
                <p className="text-sm text-text-muted">Aucune roche détectée.</p>
            ) : (
                <ul className="-mx-3 flex min-h-0 flex-1 flex-col divide-y divide-white/5 overflow-y-auto px-3 py-1">
                    {masks.map((mask) => (
                        <li key={mask.id}>
                            <button
                                type="button"
                                onClick={() => onToggle(mask.id)}
                                aria-pressed={mask.selected}
                                className="flex w-full items-center gap-3 py-3 px-3 text-left transition-colors hover:bg-white/[0.03]"
                            >
                <span
                    aria-hidden="true"
                    className={`h-2 w-2 shrink-0 rounded-full transition-shadow ${
                        mask.selected
                            ? "bg-gradient-to-br from-accent-soft to-accent shadow-[0_0_10px_rgba(192,255,137,0.6)]"
                            : "bg-white/10"
                    }`}
                />

                                <span className="flex min-w-0 flex-1 flex-col">
                  <span
                      className={`truncate text-base font-medium lg:text-[17px] ${
                          mask.selected ? "text-accent" : "text-text-title"
                      }`}
                  >
                    {mask.label}
                  </span>
                  <span className="text-xs uppercase tracking-wide text-text-muted">
                    {mask.min_dim}cm × {mask.max_dim}cm
                  </span>
                </span>
                            </button>
                        </li>
                    ))}
                </ul>
            )}
        </section>
    );
}
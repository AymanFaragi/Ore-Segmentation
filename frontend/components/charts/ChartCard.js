export default function ChartCard({ title, children }) {
    return (
        <section aria-label={title} className="flex flex-col gap-4 rounded-panel panel-surface px-6 py-6">
            <h3 className="text-lg font-light text-text-title [text-shadow:0_0_5px_rgba(208,208,208,0.25)] lg:text-xl">
                {title}
            </h3>
            <div className="w-full">{children}</div>
        </section>
    );
}
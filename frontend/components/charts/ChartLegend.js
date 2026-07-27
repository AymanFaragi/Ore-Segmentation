export default function ChartLegend({ items }) {
    return (
        <ul className="flex flex-wrap items-center justify-center gap-4 text-xs text-text-muted">
            {items.map((item) => (
                <li key={item.label} className="flex items-center gap-2">
          <span
              aria-hidden="true"
              className="h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: item.color, boxShadow: `0 0 4px ${item.color}` }}
          />
                    {item.label}
                </li>
            ))}
        </ul>
    );
}
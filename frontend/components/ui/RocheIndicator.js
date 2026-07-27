export default function RocheIndicator({ checked }) {
    return (
        <span
            aria-hidden="true"
            className="relative flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-text-body shadow-[0_0_6.2px_rgba(179,179,179,0.25)]"
        >
      {checked && (
          <span className="h-3 w-3 rounded-full bg-accent-soft shadow-[0_0_4px_#B4FF8C]" />
      )}
    </span>
    );
}
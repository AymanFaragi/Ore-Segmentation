export default function LiveFeed({ baseImage, overlays = [] }) {
    return (
        <div className="relative h-[700px] w-full overflow-hidden rounded-panel shadow-card lg:h-[700px]">
            <img
                src={baseImage}
                alt="Dernière image capturée par la caméra"
                className="absolute inset-0 h-full w-full object-cover"
            />
            {overlays.map((mask) => (
                <img
                    key={mask.id}
                    src={mask.img}
                    alt=""
                    aria-hidden="true"
                    className="pointer-events-none absolute inset-0 h-full w-full object-cover"
                />
            ))}
        </div>
    );
}
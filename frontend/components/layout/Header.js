import Image from "next/image";
import Link from "next/link";

export default function Header() {
    return (
        <header className="sticky top-0 z-20 border-b border-white/5 bg-bg-to/90 px-4 py-4 backdrop-blur-md sm:px-6 lg:px-10">
            <Link href="/" className="inline-flex w-fit items-center gap-4">
                <Image
                    src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/OCP_Group.svg/330px-OCP_Group.svg.png"
                    alt="OCP Group logo"
                    width={80}
                    height={40}
                    className="h-8 w-auto object-contain"
                />

                <span aria-hidden="true" className="h-7 w-px bg-white/10" />

                <h1 className="text-xl font-normal text-text-title">
                    Ore Segmentation
                </h1>
            </Link>
        </header>
    );
}
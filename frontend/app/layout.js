import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";
import Providers from "./providers";

const plusJakartaSans = Plus_Jakarta_Sans({
    variable: "--font-plus-jakarta-sans",
    subsets: ["latin"],
    weight: ["300", "400", "500", "600", "700"],
});

export const metadata = {
    title: "Ore Segmentation",
    description: "OCP Group | SBU Mining",
};

export default function RootLayout({ children }) {
    return (
        <html lang="fr">
        <body className={plusJakartaSans.variable}>
        <Providers>{children}</Providers>
        </body>
        </html>
    );
}
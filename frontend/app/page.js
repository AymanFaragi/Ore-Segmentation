import SkipLink from "@/components/layout/SkipLink";
import Header from "@/components/layout/Header";
import Dashboard from "@/components/dashboard/Dashboard";

export default function Home() {
    return (
        <>
            <SkipLink />
            <Header />
            <main id="main-content">
                <Dashboard />
            </main>
        </>
    );
}
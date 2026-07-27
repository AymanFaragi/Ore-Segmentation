export default function DashboardGrid({ topBar, feed, charts, sidebar }) {
    return (
        <div className="mx-auto flex w-full max-w-[1600px] flex-col gap-6 px-4 py-8 sm:px-6 lg:px-10">
            {topBar}
            <div className="flex flex-col gap-6 lg:grid lg:grid-cols-[minmax(0,1fr)_360px] lg:grid-rows-[700px_420px]">
                <div className="lg:col-start-1 lg:row-start-1">{feed}</div>

                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:col-start-1 lg:row-start-2">
                    {charts}
                </div>

                <div className="lg:col-start-2 lg:row-span-2">{sidebar}</div>
            </div>
        </div>
    );
}
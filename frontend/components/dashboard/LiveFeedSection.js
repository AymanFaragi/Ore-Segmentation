import { CONNECTION_STATUS, STREAM_STATUS } from "@/lib/constants";
import LiveFeed from "./LiveFeed";
import StreamStatusView from "./StreamStatusView";

export default function LiveFeedSection({
                                            connectionStatus,
                                            streamStatus,
                                            imageData,
                                            overlays = [],
                                            onRetry,
                                        }) {
    if (connectionStatus === CONNECTION_STATUS.DISCONNECTED) {
        return <StreamStatusView variant="disconnected" onRetry={onRetry} />;
    }

    if (streamStatus === STREAM_STATUS.DOWN) {
        return <StreamStatusView variant="down" />;
    }

    if (streamStatus === STREAM_STATUS.STARTING || !imageData) {
        return <StreamStatusView variant="starting" />;
    }

    return <LiveFeed baseImage={imageData} overlays={overlays} />;
}
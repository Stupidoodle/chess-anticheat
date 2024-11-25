class BehavioralCollector {
    private mouseEvents: MouseEvent[] = [];
    private tabEvents: TabEvent[] = [];
    private config: CollectorConfig;
    private lastActiveTimestamp: number;

    constructor(config: CollectorConfig) {
        this.config = config;
        this.lastActiveTimestamp = Date.now();
        this.initializeListeners();
        this.startPeriodicSend();
    }

    private initializeListeners(): void {
        // Mouse movement tracking
        document.addEventListener('mousemove', this.handleMouseMove);
        document.addEventListener('mousedown', this.handleMouseDown);
        document.addEventListener('mouseup', this.handleMouseUp);

        // Tab switching detection
        document.addEventListener('visibilitychange', this.handleVisibilityChange);

        // Window focus
        window.addEventListener('focus', this.handleWindowFocus);
        window.addEventListener('blur', this.handleWindowBlur);
    }

    private handleMouseMove = (event: MouseEvent): void => {
        const currentTime = Date.now();

        // Only record if sufficient time has passed (throttling)
        if (currentTime - this.lastActiveTimestamp > 50) {
            this.mouseEvents.push({
                x: event.clientX,
                y: event.clientY,
                timestamp: currentTime,
                gamePhase: this.getCurrentGamePhase(),
                squareHovered: this.getHoveredSquare(event),
                pieceSelected: this.getSelectedPiece()
            });

            this.lastActiveTimestamp = currentTime;
            this.checkBatchSize();
        }
    }

    private getHoveredSquare(event: MouseEvent): string | undefined {
        // Convert mouse coordinates to chess square (e.g., "e4")
        const board = document.querySelector('.chessboard');
        if (!board) return undefined;

        const rect = board.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        // Calculate square coordinates
        const file = Math.floor(x / (rect.width / 8));
        const rank = 7 - Math.floor(y / (rect.height / 8));

        if (file >= 0 && file < 8 && rank >= 0 && rank < 8) {
            return `${String.fromCharCode(97 + file)}${rank + 1}`;
        }
        return undefined;
    }

    private async sendBatch(): Promise<void> {
        if (this.mouseEvents.length === 0 && this.tabEvents.length === 0) return;

        try {
            const response = await fetch('/api/behavioral/collect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    gameId: this.config.gameId,
                    mouseEvents: this.mouseEvents,
                    tabEvents: this.tabEvents,
                    timestamp: Date.now()
                })
            });

            if (response.ok) {
                this.mouseEvents = [];
                this.tabEvents = [];
            }
        } catch (error) {
            console.error('Failed to send behavioral data:', error);
        }
    }
}

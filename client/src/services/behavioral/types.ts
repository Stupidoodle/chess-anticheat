interface MouseEvent {
    x: number;
    y: number;
    timestamp: number;
    gamePhase: string;
    pieceSelected?: string;
    squareHovered?: string;
}

interface TabEvent {
    type: 'focus' | 'blur';
    timestamp: number;
    duration?: number;
}

interface CollectorConfig {
    batchSize: number;
    sendInterval: number;
    gameId: string;
}

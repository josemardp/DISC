export interface TelemetryBlockData {
  blockNumber: number;
  startTime: number;
  firstClickTime: number | null;
  endTime: number | null;
  rviCount: number;
  clicks: Array<{ itemId: number; value: number; timestamp: number }>;
}

class TelemetryTracker {
  private activeBlock: number | null = null;
  private blockStartTime: number = 0;
  private firstClickTime: number | null = null;
  private rviCount: number = 0;
  private clicks: Array<{ itemId: number; value: number; timestamp: number }> = [];

  private blocksData: Record<number, TelemetryBlockData> = {};

  startBlock(blockNumber: number) {
    this.activeBlock = blockNumber;
    this.blockStartTime = Date.now();
    this.firstClickTime = null;
    this.rviCount = 0;
    this.clicks = [];
  }

  recordClick(itemId: number, value: number) {
    if (this.activeBlock === null) return;
    
    const now = Date.now();
    
    // Registra TTFC (Time to First Click)
    if (this.firstClickTime === null) {
      this.firstClickTime = now - this.blockStartTime;
    } else {
      // Se já clicou antes, qualquer clique subsequente incrementa o RVI (Response Volatility Index)
      this.rviCount += 1;
    }
    
    this.clicks.push({
      itemId,
      value,
      timestamp: now - this.blockStartTime
    });
  }

  endBlock(blockNumber: number) {
    if (this.activeBlock !== blockNumber) return;
    
    const now = Date.now();
    this.blocksData[blockNumber] = {
      blockNumber,
      startTime: this.blockStartTime,
      firstClickTime: this.firstClickTime,
      endTime: now - this.blockStartTime, // Item Response Time (IRT)
      rviCount: this.rviCount,
      clicks: [...this.clicks]
    };
    
    this.activeBlock = null;
  }

  getSummary(): { ttfcAvg: number; irtAvg: number; rviCount: number; raw: TelemetryBlockData[] } {
    const list = Object.values(this.blocksData);
    if (list.length === 0) {
      return { ttfcAvg: 0, irtAvg: 0, rviCount: 0, raw: [] };
    }
    
    let totalTtfc = 0;
    let validTtfcCount = 0;
    let totalIrt = 0;
    let totalRvi = 0;
    
    list.forEach(b => {
      if (b.firstClickTime !== null) {
        totalTtfc += b.firstClickTime;
        validTtfcCount += 1;
      }
      if (b.endTime !== null) {
        totalIrt += b.endTime;
      }
      totalRvi += b.rviCount;
    });
    
    return {
      ttfcAvg: Math.round(validTtfcCount > 0 ? totalTtfc / validTtfcCount : 0),
      irtAvg: Math.round(totalIrt / list.length),
      rviCount: totalRvi,
      raw: list
    };
  }

  clear() {
    this.activeBlock = null;
    this.blocksData = {};
  }
}

export const telemetryTracker = new TelemetryTracker();

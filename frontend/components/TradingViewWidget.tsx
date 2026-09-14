"use client";

import Script from "next/script";
import { useId } from "react";
import { TRADINGVIEW_SYMBOL_MAP } from "@/lib/api";

declare global {
  interface Window {
    TradingView?: {
      widget: new (options: Record<string, unknown>) => unknown;
    };
  }
}

export default function TradingViewWidget({ symbol, height = 480 }: { symbol: string; height?: number }) {
  const reactId = useId().replace(/[^a-zA-Z0-9]/g, "");
  const containerId = `tv_${reactId}`;
  const tvSymbol = TRADINGVIEW_SYMBOL_MAP[symbol] || symbol;

  function initWidget() {
    if (window.TradingView) {
      new window.TradingView.widget({
        autosize: true,
        symbol: tvSymbol,
        interval: "60",
        timezone: "Etc/UTC",
        theme: "dark",
        style: "1",
        locale: "en",
        enable_publishing: false,
        hide_top_toolbar: false,
        hide_legend: false,
        save_image: false,
        container_id: containerId,
      });
    }
  }

  return (
    <div className="panel" style={{ padding: 0, overflow: "hidden" }}>
      <div id={containerId} style={{ height }} />
      <Script src="https://s3.tradingview.com/tv.js" strategy="afterInteractive" onReady={initWidget} onLoad={initWidget} />
    </div>
  );
}

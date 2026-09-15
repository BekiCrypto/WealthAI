"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, SYMBOL_LABELS } from "@/lib/api";
import type { ScoreBreakdown, TechnicalSnapshot, TradeSetup } from "@/lib/types";
import { directionClass, formatNumber } from "@/lib/format";
import TradingViewWidget from "@/components/TradingViewWidget";
import TradeSetupCard from "@/components/TradeSetupCard";

export default function AssetDetailPage() {
  const params = useParams<{ symbol: string }>();
  const symbol = decodeURIComponent(params.symbol);

  const [score, setScore] = useState<ScoreBreakdown | null>(null);
  const [technical, setTechnical] = useState<TechnicalSnapshot | null>(null);
  const [setup, setSetup] = useState<TradeSetup | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [s, t, ts] = await Promise.all([api.assetScore(symbol), api.assetTechnical(symbol), api.assetSetup(symbol)]);
        if (cancelled) return;
        setScore(s);
        setTechnical(t);
        setSetup(ts);
        setError(null);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load asset data");
      }
    }
    load();
    const id = setInterval(load, 60_000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [symbol]);

  const label = SYMBOL_LABELS[symbol] || symbol;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div>
        <h1 style={{ fontSize: 24 }}>{label}</h1>
        <span className="text-dim mono text-sm">{symbol}</span>
      </div>

      <TradingViewWidget symbol={symbol} />

      {error && <div style={{ color: "var(--bearish)" }}>{error}</div>}

      {setup && <TradeSetupCard setup={setup} />}

      {technical && (
        <div className="panel">
          <div className="section-title">Technical Snapshot</div>
          <div className="grid grid-cols-4">
            <Stat label="Trend" value={technical.trend.replace(/_/g, " ")} />
            <Stat label="RSI (14)" value={formatNumber(technical.rsi_14)} />
            <Stat label="20D Volatility (ann.)" value={technical.volatility_20d ? `${(technical.volatility_20d * 100).toFixed(1)}%` : "—"} />
            {technical.redistributable && <Stat label="Last Price" value={formatNumber(technical.last_price)} />}
            {technical.redistributable && <Stat label="ATR (14)" value={formatNumber(technical.atr_14)} />}
            {technical.redistributable && <Stat label="SMA 20" value={formatNumber(technical.sma_20)} />}
            {technical.redistributable && <Stat label="SMA 50" value={formatNumber(technical.sma_50)} />}
            {technical.redistributable && <Stat label="SMA 200" value={formatNumber(technical.sma_200)} />}
            {technical.redistributable && <Stat label="EMA 20" value={formatNumber(technical.ema_20)} />}
            {technical.redistributable && <Stat label="Support" value={formatNumber(technical.support)} />}
            {technical.redistributable && <Stat label="Resistance" value={formatNumber(technical.resistance)} />}
          </div>
          {!technical.redistributable && technical.price_disclosure && (
            <div className="text-dim text-sm" style={{ marginTop: 14 }}>
              {technical.price_disclosure}
            </div>
          )}
        </div>
      )}

      {score && (
        <div className="panel">
          <div className="section-title">Intelligence Score</div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginBottom: 14 }}>
            <span className="mono" style={{ fontSize: 32, fontWeight: 700 }}>
              {score.bullish_pct}%
            </span>
            <span className="text-dim">bullish</span>
            <span className="tag">{score.confidence} confidence</span>
          </div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
            <span className={`tag ${directionClass(score.macro)}`}>Macro: {score.macro}</span>
            <span className={`tag ${directionClass(score.technical)}`}>Technical: {score.technical}</span>
            <span className={`tag ${directionClass(score.sentiment)}`}>Sentiment: {score.sentiment}</span>
            <span className={`tag ${directionClass(score.geopolitical)}`}>Geopolitical: {score.geopolitical}</span>
          </div>
          <div className="section-title">Why</div>
          <ul style={{ margin: 0, paddingLeft: 18, display: "flex", flexDirection: "column", gap: 6 }}>
            {score.reasons.map((r, i) => (
              <li key={i} className="text-sm">
                {r}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <span className="text-dim text-sm">{label}</span>
      <span className="mono">{value}</span>
    </div>
  );
}

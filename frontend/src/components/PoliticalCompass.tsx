import React, { useState, useEffect } from 'react';
import { Compass, Info, Users, ExternalLink, Filter } from 'lucide-react';
import { api } from '../api/client';
import type { CompassParty } from '../types';

interface PoliticalCompassProps {
  onSelectParty: (partyId: string) => void;
  userStatementPoint?: { x: number; y: number; label: string } | null;
}

export const PoliticalCompass: React.FC<PoliticalCompassProps> = ({ onSelectParty, userStatementPoint }) => {
  const [parties, setParties] = useState<CompassParty[]>([]);
  const [filterParliamentOnly, setFilterParliamentOnly] = useState<boolean>(false);
  const [hoveredParty, setHoveredParty] = useState<CompassParty | null>(null);
  const [selectedParty, setSelectedParty] = useState<CompassParty | null>(null);

  useEffect(() => {
    api.getCompass()
      .then(res => setParties(res.parties))
      .catch(() => {});
  }, []);

  const displayParties = filterParliamentOnly
    ? parties.filter(p => p.inParliament)
    : parties;

  // SVG dimensions & coordinate conversion
  const width = 640;
  const height = 640;
  const padding = 50;
  const innerWidth = width - padding * 2;
  const innerHeight = height - padding * 2;

  // Converts coordinate (-10 to +10) to SVG pixel
  const getX = (val: number) => padding + ((val + 10) / 20) * innerWidth;
  // Y-axis inverted in SVG: +10 is top, -10 is bottom
  const getY = (val: number) => padding + ((10 - val) / 20) * innerHeight;

  return (
    <div className="space-y-6">
      {/* Title & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300 text-xs font-semibold mb-2">
            <Compass className="w-3.5 h-3.5" />
            2D Ideologische Matrix (2023 - 2026)
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Het Nederlandse Politieke Kieskompas
          </h2>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1 max-w-2xl">
            Visueel overzicht van de politieke verhoudingen in Nederland. Gebaseerd op stemgedrag,
            partijprogramma's en politicologische consensus langs de economische en sociaal-culturele as.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setFilterParliamentOnly(!filterParliamentOnly)}
            className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold transition-colors cursor-pointer border ${
              filterParliamentOnly
                ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                : 'bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800'
            }`}
          >
            <Filter className="w-3.5 h-3.5" />
            <span>{filterParliamentOnly ? 'Alleen Tweede Kamer (15)' : 'Alle 24 Partijen'}</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Compass + Interactive Details Card */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* SVG Compass Container */}
        <div className="lg:col-span-8 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-4 sm:p-6 shadow-sm flex flex-col items-center">
          <div className="relative w-full max-w-[640px] aspect-square">
            <svg
              viewBox={`0 0 ${width} ${height}`}
              className="w-full h-full select-none"
            >
              {/* Quadrant Backgrounds */}
              {/* Top-Left: Progressief Links */}
              <rect
                x={padding}
                y={padding}
                width={innerWidth / 2}
                height={innerHeight / 2}
                fill="currentColor"
                className="text-emerald-500/5 dark:text-emerald-500/10"
              />
              {/* Top-Right: Progressief Rechts */}
              <rect
                x={padding + innerWidth / 2}
                y={padding}
                width={innerWidth / 2}
                height={innerHeight / 2}
                fill="currentColor"
                className="text-blue-500/5 dark:text-blue-500/10"
              />
              {/* Bottom-Left: Conservatief Links */}
              <rect
                x={padding}
                y={padding + innerHeight / 2}
                width={innerWidth / 2}
                height={innerHeight / 2}
                fill="currentColor"
                className="text-rose-500/5 dark:text-rose-500/10"
              />
              {/* Bottom-Right: Conservatief Rechts */}
              <rect
                x={padding + innerWidth / 2}
                y={padding + innerHeight / 2}
                width={innerWidth / 2}
                height={innerHeight / 2}
                fill="currentColor"
                className="text-amber-500/5 dark:text-amber-500/10"
              />

              {/* Grid Lines */}
              {[-8, -6, -4, -2, 2, 4, 6, 8].map(v => (
                <g key={`grid-${v}`}>
                  <line
                    x1={getX(v)}
                    y1={padding}
                    x2={getX(v)}
                    y2={height - padding}
                    stroke="currentColor"
                    strokeDasharray="2,3"
                    className="text-slate-200 dark:text-slate-800"
                    strokeWidth="1"
                  />
                  <line
                    x1={padding}
                    y1={getY(v)}
                    x2={width - padding}
                    y2={getY(v)}
                    stroke="currentColor"
                    strokeDasharray="2,3"
                    className="text-slate-200 dark:text-slate-800"
                    strokeWidth="1"
                  />
                </g>
              ))}

              {/* Main Axes */}
              {/* Horizontal X Axis */}
              <line
                x1={padding}
                y1={height / 2}
                x2={width - padding}
                y2={height / 2}
                stroke="currentColor"
                className="text-slate-400 dark:text-slate-600"
                strokeWidth="2"
              />
              {/* Vertical Y Axis */}
              <line
                x1={width / 2}
                y1={padding}
                x2={width / 2}
                y2={height - padding}
                stroke="currentColor"
                className="text-slate-400 dark:text-slate-600"
                strokeWidth="2"
              />

              {/* Outer Border */}
              <rect
                x={padding}
                y={padding}
                width={innerWidth}
                height={innerHeight}
                fill="none"
                stroke="currentColor"
                className="text-slate-300 dark:text-slate-700"
                strokeWidth="1.5"
                rx="6"
              />

              {/* Quadrant Labels */}
              <text x={padding + 14} y={padding + 22} className="text-[11px] font-bold fill-emerald-600 dark:fill-emerald-400 uppercase tracking-wider opacity-70">
                Progressief-Links
              </text>
              <text x={width - padding - 14} y={padding + 22} textAnchor="end" className="text-[11px] font-bold fill-blue-600 dark:fill-blue-400 uppercase tracking-wider opacity-70">
                Progressief-Rechts
              </text>
              <text x={padding + 14} y={height - padding - 14} className="text-[11px] font-bold fill-rose-600 dark:fill-rose-400 uppercase tracking-wider opacity-70">
                Conservatief-Links
              </text>
              <text x={width - padding - 14} y={height - padding - 14} textAnchor="end" className="text-[11px] font-bold fill-amber-600 dark:fill-amber-400 uppercase tracking-wider opacity-70">
                Conservatief-Rechts
              </text>

              {/* Axis End Labels */}
              <text x={padding} y={height / 2 - 8} className="text-[11px] font-extrabold fill-slate-700 dark:fill-slate-300">
                ◄ LINKS
              </text>
              <text x={width - padding} y={height / 2 - 8} textAnchor="end" className="text-[11px] font-extrabold fill-slate-700 dark:fill-slate-300">
                RECHTS ►
              </text>
              <text x={width / 2 + 8} y={padding + 12} className="text-[11px] font-extrabold fill-slate-700 dark:fill-slate-300">
                ▲ PROGRESSIEF
              </text>
              <text x={width / 2 + 8} y={height - padding - 6} className="text-[11px] font-extrabold fill-slate-700 dark:fill-slate-300">
                ▼ CONSERVATIEF
              </text>

              {/* Party Nodes */}
              {displayParties.map(p => {
                const cx = getX(p.x);
                const cy = getY(p.y);
                const isHovered = hoveredParty?.id === p.id;
                const isSelected = selectedParty?.id === p.id;
                // Node radius: proportional to seats with min radius 11
                const radius = Math.max(11, Math.min(22, 10 + Math.sqrt(p.seats) * 2));

                return (
                  <g
                    key={p.id}
                    className="cursor-pointer transition-transform"
                    onMouseEnter={() => setHoveredParty(p)}
                    onMouseLeave={() => setHoveredParty(null)}
                    onClick={() => {
                      setSelectedParty(p);
                      onSelectParty(p.id);
                    }}
                  >
                    {/* Glow circle on hover or selected */}
                    {(isHovered || isSelected) && (
                      <circle
                        cx={cx}
                        cy={cy}
                        r={radius + 6}
                        fill={p.color}
                        opacity="0.3"
                        className="animate-pulse"
                      />
                    )}

                    {/* Main Party Circle */}
                    <circle
                      cx={cx}
                      cy={cy}
                      r={radius}
                      fill={p.color}
                      stroke="#ffffff"
                      strokeWidth={isSelected ? '3' : '2'}
                      className="shadow-md transition-all"
                    />

                    {/* Party Abbreviation Text */}
                    <text
                      x={cx}
                      y={cy + 3.5}
                      textAnchor="middle"
                      fill={p.textColor || '#ffffff'}
                      className="text-[9.5px] font-black pointer-events-none select-none tracking-tight"
                    >
                      {p.name.length > 5 ? p.name.slice(0, 4) : p.name}
                    </text>
                  </g>
                );
              })}

              {/* Optional: User Evaluated Statement Pin */}
              {userStatementPoint && (
                <g className="cursor-pointer">
                  <circle
                    cx={getX(userStatementPoint.x)}
                    cy={getY(userStatementPoint.y)}
                    r="18"
                    fill="#3b82f6"
                    opacity="0.3"
                    className="animate-ping"
                  />
                  <circle
                    cx={getX(userStatementPoint.x)}
                    cy={getY(userStatementPoint.y)}
                    r="9"
                    fill="#2563eb"
                    stroke="#ffffff"
                    strokeWidth="2.5"
                  />
                  <text
                    x={getX(userStatementPoint.x)}
                    y={getY(userStatementPoint.y) - 13}
                    textAnchor="middle"
                    className="text-[10px] font-extrabold fill-blue-600 dark:fill-blue-400 bg-white"
                  >
                    📍 Huidige Stelling
                  </text>
                </g>
              )}
            </svg>
          </div>

          <div className="flex items-center justify-between w-full text-xs text-slate-500 dark:text-slate-400 mt-4 px-2">
            <span>Bolgrootte = Aantal zetels in de Tweede Kamer</span>
            <span>Klik op een partij om het partijdossier te openen</span>
          </div>
        </div>

        {/* Sidebar Info Card */}
        <div className="lg:col-span-4 space-y-4">
          {/* Active Highlight Card */}
          {hoveredParty || selectedParty ? (
            (() => {
              const active = hoveredParty || selectedParty!;
              return (
                <div
                  className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 shadow-md transition-all"
                  style={{ borderTopWidth: '6px', borderTopColor: active.color }}
                >
                  <div className="flex items-center justify-between mb-3">
                    <span
                      className="px-3 py-1 rounded-full text-xs font-extrabold text-white"
                      style={{ backgroundColor: active.color }}
                    >
                      {active.name}
                    </span>
                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                      {active.seats > 0 ? `${active.seats} zetels` : '0 zetels'}
                    </span>
                  </div>

                  <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-1">
                    {active.fullName}
                  </h3>

                  <div className="grid grid-cols-2 gap-2 my-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800 text-xs">
                    <div>
                      <span className="text-slate-500 dark:text-slate-400 block">Economisch:</span>
                      <strong className="text-slate-800 dark:text-slate-200">
                        {active.x > 0 ? `+${active.x} (Rechts)` : active.x < 0 ? `${active.x} (Links)` : '0 (Midden)'}
                      </strong>
                    </div>
                    <div>
                      <span className="text-slate-500 dark:text-slate-400 block">Maatschappelijk:</span>
                      <strong className="text-slate-800 dark:text-slate-200">
                        {active.y > 0 ? `+${active.y} (Prog)` : active.y < 0 ? `${active.y} (Cons)` : '0 (Midden)'}
                      </strong>
                    </div>
                  </div>

                  <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed mb-4">
                    {active.summary}
                  </p>

                  <button
                    onClick={() => onSelectParty(active.id)}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition-colors shadow-sm cursor-pointer"
                  >
                    <span>Open Volledig Dossier</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })()
          ) : (
            <div className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 shadow-sm text-center">
              <div className="w-12 h-12 rounded-full bg-blue-50 dark:bg-blue-950/60 text-blue-600 mx-auto flex items-center justify-center mb-3">
                <Info className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-slate-900 dark:text-white mb-1">
                Beweeg over een partij
              </h4>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                Hover of klik op een partij in het kompas om de exacte positie, het aantal zetels en de kernvisie te bekijken.
              </p>
            </div>
          )}

          {/* Quick Party Directory Chips */}
          <div className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 shadow-sm">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
              <Users className="w-3.5 h-3.5" /> Direct Partij Uitlichten
            </h4>
            <div className="flex flex-wrap gap-1.5 max-h-60 overflow-y-auto pr-1">
              {displayParties.map(p => (
                <button
                  key={p.id}
                  onClick={() => setSelectedParty(p)}
                  className="px-2.5 py-1 rounded-lg text-xs font-bold text-white transition-transform hover:scale-105 cursor-pointer shadow-sm"
                  style={{ backgroundColor: p.color }}
                >
                  {p.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

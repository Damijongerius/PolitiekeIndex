import React, { useState, useEffect } from 'react';
import { Search, Layers, Download, ExternalLink, ArrowUpDown } from 'lucide-react';
import { api } from '../api/client';
import type { PartySummary } from '../types';

interface PartyDirectoryProps {
  onSelectParty: (partyId: string) => void;
}

export const PartyDirectory: React.FC<PartyDirectoryProps> = ({ onSelectParty }) => {
  const [parties, setParties] = useState<PartySummary[]>([]);
  const [search, setSearch] = useState<string>('');
  const [filterCategory, setFilterCategory] = useState<'all' | 'parliament' | 'extra'>('all');
  const [sortBy, setSortBy] = useState<'seats' | 'az'>('seats');

  useEffect(() => {
    api.getParties()
      .then(setParties)
      .catch(() => {});
  }, []);

  const filtered = parties
    .filter(p => {
      if (filterCategory === 'parliament') return p.inParliament;
      if (filterCategory === 'extra') return !p.inParliament;
      return true;
    })
    .filter(p => {
      const q = search.toLowerCase();
      return (
        p.name.toLowerCase().includes(q) ||
        p.fullName.toLowerCase().includes(q) ||
        p.leader.toLowerCase().includes(q) ||
        p.orientation.toLowerCase().includes(q)
      );
    })
    .sort((a, b) => {
      if (sortBy === 'seats') {
        if (b.seats !== a.seats) return b.seats - a.seats;
        return a.name.localeCompare(b.name);
      }
      return a.name.localeCompare(b.name);
    });

  return (
    <div className="space-y-6">
      {/* Title & Controls Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300 text-xs font-semibold mb-2">
            <Layers className="w-3.5 h-3.5" />
            Officieel Partij Register
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Partij Dossiers & Verkiezingsprogramma's
          </h2>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
            Doorzoek alle {parties.length > 0 ? parties.length : 27} Nederlandse politieke partijen met hun PDF-programma's, zetels en profielen.
          </p>

        </div>

        {/* Search Bar */}
        <div className="relative min-w-[260px] sm:min-w-[320px]">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Zoek partij, lijsttrekker of stroming..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
          />
        </div>
      </div>

      {/* Filter & Sort Chips */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 dark:border-slate-800 pb-4">
        <div className="flex items-center gap-1.5">
          {[
            { id: 'all' as const, label: 'Alle Partijen', count: parties.length },
            { id: 'parliament' as const, label: 'In Tweede Kamer', count: parties.filter(p => p.inParliament).length },
            { id: 'extra' as const, label: 'Buitenparlementair', count: parties.filter(p => !p.inParliament).length },
          ].map(f => (
            <button
              key={f.id}
              onClick={() => setFilterCategory(f.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 cursor-pointer ${
                filterCategory === f.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300'
              }`}
            >
              <span>{f.label}</span>
              <span className={`px-1.5 py-0.2 rounded-full text-[10px] ${
                filterCategory === f.id ? 'bg-blue-700 text-blue-100' : 'bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300'
              }`}>
                {f.count}
              </span>
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-400 font-semibold flex items-center gap-1">
            <ArrowUpDown className="w-3.5 h-3.5" /> Sorteer:
          </span>
          <button
            onClick={() => setSortBy(sortBy === 'seats' ? 'az' : 'seats')}
            className="px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 font-semibold text-slate-700 dark:text-slate-300 cursor-pointer"
          >
            {sortBy === 'seats' ? 'Zetels (Hoog naar Laag)' : 'Alfabetisch (A - Z)'}
          </button>
        </div>
      </div>

      {/* Parties Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map(p => (
          <div
            key={p.id}
            className="group rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm hover:shadow-md hover:border-slate-300 dark:hover:border-slate-700 transition-all flex flex-col"
          >
            {/* Top Color Accent */}
            <div className="h-2 w-full" style={{ backgroundColor: p.color }} />

            <div className="p-5 flex-1 flex flex-col">
              <div className="flex items-start gap-4 mb-4">
                {/* PDF Cover Image Preview */}
                <div
                  className="w-16 h-22 rounded-lg bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shrink-0 overflow-hidden shadow-xs cursor-pointer"
                  onClick={() => onSelectParty(p.id)}
                >
                  <img
                    src={p.coverUrl}
                    alt={p.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                    onError={(e) => {
                      (e.target as HTMLElement).style.display = 'none';
                    }}
                  />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span
                      className="px-2 py-0.5 rounded text-[10px] font-black uppercase text-white shadow-xs"
                      style={{ backgroundColor: p.color }}
                    >
                      {p.name}
                    </span>
                    {p.seats > 0 ? (
                      <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                        {p.seats} zetels
                      </span>
                    ) : (
                      <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500">
                        Buitenparlementair
                      </span>
                    )}
                  </div>

                  <h3
                    className="text-base font-bold text-slate-900 dark:text-white truncate cursor-pointer hover:text-blue-600 transition-colors"
                    onClick={() => onSelectParty(p.id)}
                  >
                    {p.fullName}
                  </h3>

                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                    Lijsttrekker: <strong className="text-slate-700 dark:text-slate-300">{p.leader}</strong>
                  </p>
                </div>
              </div>

              {/* Orientation and Short Description */}
              <div className="mb-4 flex-1">
                <span className="inline-block text-[11px] font-semibold text-blue-700 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-2 py-0.5 rounded mb-2">
                  {p.orientation}
                </span>
                <p className="text-xs text-slate-600 dark:text-slate-300 line-clamp-3 leading-relaxed">
                  {p.shortDescription}
                </p>
              </div>

              {/* Bottom Action Footer */}
              <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between gap-2 mt-auto">
                <button
                  onClick={() => onSelectParty(p.id)}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition-colors cursor-pointer shadow-sm"
                >
                  <span>Bekijk Dossier</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </button>

                <a
                  href={p.pdfUrl}
                  download
                  title="Download officiële PDF"
                  className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 hover:text-slate-900 hover:bg-slate-100 dark:text-slate-400 dark:hover:text-white dark:hover:bg-slate-800 transition-colors"
                >
                  <Download className="w-4 h-4" />
                </a>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

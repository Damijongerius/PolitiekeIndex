import React, { useState, useEffect } from 'react';
import {
  Search, RefreshCw, ExternalLink, Globe, Users,
  Award, Building2, ChevronDown, ChevronUp, Sparkles, BookOpen, Loader2
} from 'lucide-react';
import { api } from '../api/client';
import type { TweedeKamerResponse } from '../types';


interface TweedeKamerFractiesProps {
  onSelectParty: (partyId: string) => void;
}

// Approximate party colors for parliament bar
const PARTY_COLORS: Record<string, string> = {
  'd66': '#00a651',
  'vvd': '#0052cc',
  'gl-pvda': '#e11d48',
  'pro': '#e11d48',
  'pvv': '#002855',
  'cda': '#007b5f',
  'ja21': '#18335b',
  'fvd': '#841818',
  'groep-markuszower': '#1e3a8a',
  'bbb': '#8cb811',
  'denk': '#00a19c',
  'sgp': '#ea580c',
  'pvdd': '#006b38',
  'christenunie': '#00a3e0',
  'sp': '#ee1c25',
  '50plus': '#9333ea',
  'volt': '#502379',
  'lid-keijzer': '#65a30d',
};

export const TweedeKamerFracties: React.FC<TweedeKamerFractiesProps> = ({ onSelectParty }) => {
  const [data, setData] = useState<TweedeKamerResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [scraping, setScraping] = useState<boolean>(false);
  const [search, setSearch] = useState<string>('');
  const [expandedFracties, setExpandedFracties] = useState<Record<string, boolean>>({});
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const loadData = (refresh = false) => {
    setLoading(true);
    api.getTweedeKamerFracties(refresh)
      .then(res => {
        setData(res);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadData(false);
  }, []);

  const handleScrape = async () => {
    setScraping(true);
    setStatusMessage('Live gegevens aan het ophalen van tweedekamer.nl...');
    try {
      const res = await api.triggerScrape();
      setData(res);
      setStatusMessage('Succesvol bijgewerkt vanaf de officiële website!');
      setTimeout(() => setStatusMessage(null), 4000);
    } catch (err) {
      console.error(err);
      setStatusMessage('Fout bij het ophalen van gegevens van tweedekamer.nl');
      setTimeout(() => setStatusMessage(null), 4000);
    } finally {
      setScraping(false);
    }
  };

  const toggleExpand = (id: string) => {
    setExpandedFracties(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const fracties = data?.fracties || [];

  const filtered = fracties.filter(f => {
    const q = search.toLowerCase();
    const matchesParty = f.name.toLowerCase().includes(q) || (f.leader && f.leader.toLowerCase().includes(q));
    const matchesMember = f.members.some(m => m.name.toLowerCase().includes(q));
    return matchesParty || matchesMember;
  });

  if (loading && !data) {

    return (
      <div className="py-24 flex flex-col items-center justify-center gap-3">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <p className="text-sm font-semibold text-slate-500">
          Tweede Kamer fracties en zetels inladen...
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-300">

      {/* Top Banner / Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-950/70 dark:text-blue-300 text-xs font-semibold">
            <Building2 className="w-3.5 h-3.5" />
            Officiële Parlementaire Gegevens
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Tweede Kamer der Staten-Generaal
          </h1>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Live zetelverdeling, fractievoorzitters en alle 150 Kamerleden rechtstreeks van{' '}
            <a
              href="https://www.tweedekamer.nl/kamerleden_en_commissies/fracties"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 dark:text-blue-400 underline inline-flex items-center gap-1 hover:text-blue-800"
            >
              tweedekamer.nl <ExternalLink className="w-3 h-3" />
            </a>
          </p>
          {data?.lastUpdated && (
            <p className="text-xs text-slate-400 dark:text-slate-500 pt-1">
              Laatst gesynchroniseerd: {new Date(data.lastUpdated).toLocaleString('nl-NL')}
            </p>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handleScrape}
            disabled={scraping}
            className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm shadow-sm flex items-center gap-2 cursor-pointer transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${scraping ? 'animate-spin' : ''}`} />
            {scraping ? 'Aan het scrapen...' : 'Live Scraper Uitvoeren'}
          </button>
        </div>
      </div>

      {statusMessage && (
        <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 text-blue-900 dark:bg-blue-950/50 dark:border-blue-900 dark:text-blue-200 text-sm font-medium flex items-center gap-2 animate-in fade-in">
          <Sparkles className="w-4 h-4 text-blue-600 shrink-0" />
          <span>{statusMessage}</span>
        </div>
      )}

      {/* Visual Parliament Distribution (Zetelbalk 150 Zetels) */}
      <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Award className="w-5 h-5 text-amber-500" />
              Zetelverdeling (150 Zetels Totaal)
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Meerderheid vereist: 76 zetels voor een kabinets- of motiemeerderheid
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs font-semibold">
            <span className="px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
              17 Fracties
            </span>
            <span className="px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
              150 Kamerleden
            </span>
          </div>
        </div>

        {/* 150 Seats Bar */}
        <div className="space-y-1.5">
          <div className="w-full h-8 rounded-xl bg-slate-100 dark:bg-slate-800 overflow-hidden flex shadow-inner border border-slate-200/50 dark:border-slate-700/50">
            {fracties.map(f => {
              const pct = (f.seats / 150) * 100;
              const color = PARTY_COLORS[f.id] || '#64748b';
              return (
                <div
                  key={f.id}
                  style={{ width: `${pct}%`, backgroundColor: color }}
                  title={`${f.name}: ${f.seats} zetels (${pct.toFixed(1)}%)`}
                  className="h-full transition-all hover:opacity-90 relative group cursor-pointer"
                  onClick={() => toggleExpand(f.id)}
                />
              );
            })}
          </div>
          <div className="flex justify-between text-[11px] text-slate-400 dark:text-slate-500 font-mono">
            <span>0</span>
            <span className="text-amber-600 dark:text-amber-400 font-bold">| 76 (Meerderheid)</span>
            <span>150 Zetels</span>
          </div>
        </div>

        {/* Mini Legend of Top Parties */}
        <div className="flex flex-wrap gap-2 pt-2">
          {fracties.slice(0, 8).map(f => (
            <div
              key={f.id}
              onClick={() => toggleExpand(f.id)}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/50 text-xs cursor-pointer hover:border-blue-400 transition-colors"
            >
              <div
                className="w-2.5 h-2.5 rounded-full shrink-0"
                style={{ backgroundColor: PARTY_COLORS[f.id] || '#64748b' }}
              />
              <span className="font-semibold text-slate-800 dark:text-slate-200">{f.name}</span>
              <span className="text-slate-500 font-bold">({f.seats})</span>
            </div>
          ))}
        </div>
      </div>

      {/* Search Input */}
      <div className="relative max-w-md">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Zoek fractie, fractievoorzitter of Kamerlid..."
          className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
        />
      </div>

      {/* Fracties Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map(f => {
          const isExpanded = expandedFracties[f.id];
          const color = PARTY_COLORS[f.id] || '#1e3a8a';

          return (
            <div
              key={f.id}
              className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md transition-shadow overflow-hidden flex flex-col"
            >
              {/* Card Header */}
              <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-start justify-between gap-4">
                <div className="space-y-1">
                  {f.logo && (
                    <div className="h-10 mb-3 flex items-center">
                      <img
                        src={f.logo}
                        alt={`Logo ${f.name}`}
                        className="max-h-10 max-w-[140px] object-contain"
                        onError={(e) => { (e.target as HTMLElement).style.display = 'none'; }}
                      />
                    </div>
                  )}
                  <h3 className="font-bold text-lg text-slate-900 dark:text-white leading-tight">
                    {f.name}
                  </h3>
                  {f.fullTitle && f.fullTitle !== f.name && (
                    <p className="text-xs text-slate-500">{f.fullTitle}</p>
                  )}
                </div>

                <div className="shrink-0 flex flex-col items-end gap-1">
                  <div
                    className="px-3 py-1.5 rounded-xl text-white font-extrabold text-sm shadow-sm flex items-center gap-1.5"
                    style={{ backgroundColor: color }}
                  >
                    <span>{f.seats}</span>
                    <span className="text-xs font-semibold">{f.seats === 1 ? 'Zetel' : 'Zetels'}</span>
                  </div>
                  <span className="text-[10px] text-slate-400">
                    {((f.seats / 150) * 100).toFixed(1)}% v/d Kamer
                  </span>
                </div>
              </div>

              {/* Leader Info */}
              {f.leader && (
                <div className="px-6 py-4 bg-slate-50 dark:bg-slate-800/40 border-b border-slate-100 dark:border-slate-800 flex items-center gap-3">
                  {f.leaderPhoto ? (
                    <img
                      src={f.leaderPhoto}
                      alt={f.leader}
                      className="w-12 h-12 rounded-full object-cover border border-slate-200 dark:border-slate-700 shadow-sm"
                    />
                  ) : (
                    <div className="w-12 h-12 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center font-bold text-slate-600">
                      {f.leader.charAt(0)}
                    </div>
                  )}
                  <div>
                    <span className="text-[11px] font-semibold text-blue-600 dark:text-blue-400 block uppercase tracking-wider">
                      {f.leaderRole || 'Fractievoorzitter'}
                    </span>
                    <span className="font-bold text-slate-900 dark:text-white text-sm">
                      {f.leader}
                    </span>
                  </div>
                </div>
              )}

              {/* Contact Links */}
              <div className="p-6 space-y-3 flex-1">
                <div className="flex flex-wrap gap-2 text-xs">
                  {f.website && (
                    <a
                      href={f.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 font-medium transition-colors"
                    >
                      <Globe className="w-3.5 h-3.5 text-blue-500" />
                      Website
                      <ExternalLink className="w-3 h-3 ml-0.5 opacity-60" />
                    </a>
                  )}

                  {f.detailUrl && (
                    <a
                      href={f.detailUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 font-medium transition-colors"
                    >
                      <Building2 className="w-3.5 h-3.5 text-slate-500" />
                      Tweede Kamer Pagina
                      <ExternalLink className="w-3 h-3 ml-0.5 opacity-60" />
                    </a>
                  )}
                </div>

                {/* Kamerleden Toggle */}
                {f.members && f.members.length > 0 && (
                  <div className="pt-2">
                    <button
                      onClick={() => toggleExpand(f.id)}
                      className="w-full py-2 px-3 rounded-xl bg-slate-50 dark:bg-slate-800/80 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-300 flex items-center justify-between transition-colors cursor-pointer"
                    >
                      <span className="flex items-center gap-2">
                        <Users className="w-3.5 h-3.5 text-blue-600" />
                        Kamerleden bekijken ({f.members.length})
                      </span>
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>

                    {/* Expanded Members List */}
                    {isExpanded && (
                      <div className="mt-3 max-h-60 overflow-y-auto space-y-2 pr-1 divide-y divide-slate-100 dark:divide-slate-800">
                        {f.members.map((m, idx) => (
                          <div key={idx} className="pt-2 flex items-center gap-2.5">
                            {m.photo ? (
                              <img
                                src={m.photo}
                                alt={m.name}
                                className="w-7 h-7 rounded-full object-cover shrink-0 border border-slate-200"
                              />
                            ) : (
                              <div className="w-7 h-7 rounded-full bg-slate-200 text-[10px] flex items-center justify-center font-bold text-slate-600 shrink-0">
                                {m.name.charAt(0)}
                              </div>
                            )}
                            <div className="flex-1 min-w-0">
                              {m.link ? (
                                <a
                                  href={m.link}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-xs font-medium text-slate-800 dark:text-slate-200 hover:text-blue-600 truncate block"
                                >
                                  {m.name}
                                </a>
                              ) : (
                                <span className="text-xs font-medium text-slate-800 dark:text-slate-200 truncate block">
                                  {m.name}
                                </span>
                              )}
                              <span className="text-[10px] text-slate-400 block">{m.role}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Footer Button: View Dossier */}
              <div className="p-4 bg-slate-50 dark:bg-slate-800/20 border-t border-slate-100 dark:border-slate-800">
                <button
                  onClick={() => onSelectParty(f.id)}
                  className="w-full py-2 px-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-blue-500 dark:hover:border-blue-500 text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center justify-center gap-1.5 transition-colors cursor-pointer shadow-2xs"
                >
                  <BookOpen className="w-3.5 h-3.5 text-blue-600" />
                  Bekijk Partij Dossier & Standpunten
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

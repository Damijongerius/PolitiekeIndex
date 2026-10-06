import React, { useState, useEffect } from 'react';
import {
  Search, Sparkles, BookOpen, ChevronDown, ChevronUp,
  ExternalLink, CheckCircle2, XCircle, MinusCircle, HelpCircle,
  Loader2, Filter, Compass
} from 'lucide-react';
import { api } from '../api/client';
import type { StatementEvaluationResponse, PartyStance, PresetStatement } from '../types';

interface StellingCheckerProps {
  onSelectParty: (partyId: string) => void;
  onViewOnCompass?: (point: { x: number; y: number; label: string }) => void;
}

export const StellingChecker: React.FC<StellingCheckerProps> = ({ onSelectParty, onViewOnCompass }) => {
  const [statement, setStatement] = useState<string>('');
  const [presets, setPresets] = useState<PresetStatement[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [result, setResult] = useState<StatementEvaluationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filterStance, setFilterStance] = useState<'all' | 'pro' | 'neutral' | 'against' | 'unknown'>('all');
  const [expandedQuotes, setExpandedQuotes] = useState<Record<string, boolean>>({});

  useEffect(() => {
    api.getPresets()
      .then(setPresets)
      .catch(() => {});
  }, []);

  const handleEvaluate = async (stmtToEvaluate?: string) => {
    const text = (stmtToEvaluate || statement).trim();
    if (!text) return;

    setIsLoading(true);
    setError(null);
    try {
      const data = await api.evaluateStatement(text);
      setResult(data);
      // Auto expand first 2 parties with quotes
      const initialExpanded: Record<string, boolean> = {};
      data.party_stances.forEach((ps, idx) => {
        if (idx < 2 && ps.quotes && ps.quotes.length > 0) {
          initialExpanded[ps.party_id] = true;
        }
      });
      setExpandedQuotes(initialExpanded);
    } catch (err: any) {
      setError(err.message || 'Er is een fout opgetreden bij het analyseren van de stelling.');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleQuotes = (partyId: string) => {
    setExpandedQuotes(prev => ({ ...prev, [partyId]: !prev[partyId] }));
  };

  // Filter parties by selected tab
  const filteredParties = result ? result.party_stances.filter(ps => {
    if (filterStance === 'all') return true;
    if (filterStance === 'pro') return ps.score !== null && ps.score >= 0.5;
    if (filterStance === 'neutral') return ps.score !== null && ps.score > -0.5 && ps.score < 0.5;
    if (filterStance === 'against') return ps.score !== null && ps.score <= -0.5;
    if (filterStance === 'unknown') return ps.is_unknown || ps.score === null;
    return true;
  }) : [];

  const getScoreBadge = (ps: PartyStance) => {
    if (ps.is_unknown || ps.score === null) {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
          <HelpCircle className="w-3.5 h-3.5" />
          ? Onbekend / Niet vermeld
        </span>
      );
    }
    if (ps.score >= 1.5) {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
          +2 Sterk Voor
        </span>
      );
    }
    if (ps.score >= 0.5) {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-teal-100 text-teal-800 dark:bg-teal-950/60 dark:text-teal-300 border border-teal-300 dark:border-teal-700">
          <CheckCircle2 className="w-3.5 h-3.5 text-teal-600" />
          +1 Gematigd Voor
        </span>
      );
    }
    if (ps.score > -0.5) {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 border border-amber-300 dark:border-amber-700">
          <MinusCircle className="w-3.5 h-3.5 text-amber-600" />
          0 Neutraal / Balans
        </span>
      );
    }
    if (ps.score > -1.5) {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-orange-100 text-orange-800 dark:bg-orange-950/60 dark:text-orange-300 border border-orange-300 dark:border-orange-700">
          <XCircle className="w-3.5 h-3.5 text-orange-600" />
          -1 Gematigd Tegen
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300 border border-rose-300 dark:border-rose-700">
        <XCircle className="w-3.5 h-3.5 text-rose-600" />
        -2 Sterk Tegen
      </span>
    );
  };

  return (
    <div className="space-y-8">
      {/* Hero Search Section */}
      <div className="relative rounded-2xl bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 text-white p-6 sm:p-10 shadow-xl overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(59,130,246,0.15),transparent_50%)]" />
        
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 text-xs font-semibold mb-4 border border-blue-400/20">
            <Sparkles className="w-3.5 h-3.5" />
            AI Semantic Search over 24 Verkiezingsprogramma's
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white mb-3">
            Onderzoek elk standpunt in seconden
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed mb-6">
            Typ een politieke stelling of kies een actueel maatschappelijk vraagstuk. Ons AI-systeem doorzoekt 
            duizenden pagina's aan officiële partijprogramma's, kent scores toe van <strong className="text-white">-2 tot +2</strong> en toont de exacte geciteerde PDF-passages.
          </p>

          {/* Search Box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleEvaluate();
            }}
            className="flex flex-col sm:flex-row gap-2"
          >
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                value={statement}
                onChange={(e) => setStatement(e.target.value)}
                placeholder="Bijv: 'Er moeten per direct meer kerncentrales gebouwd worden in Nederland.'"
                className="w-full pl-12 pr-4 py-3.5 rounded-xl bg-white/10 dark:bg-slate-800/80 border border-white/20 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm shadow-inner"
              />
            </div>
            <button
              type="submit"
              disabled={isLoading || !statement.trim()}
              className="px-6 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 active:bg-blue-700 disabled:opacity-50 text-white font-semibold text-sm transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-600/30 whitespace-nowrap cursor-pointer"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Doorzoeken...</span>
                </>
              ) : (
                <>
                  <span>Analyseer Stelling</span>
                  <Sparkles className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Quick Presets */}
          <div className="mt-5">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2.5">
              💡 Populaire Voorbeeld Stellingen:
            </p>
            <div className="flex flex-wrap gap-2">
              {presets.map((p) => (
                <button
                  key={p.id}
                  onClick={() => {
                    setStatement(p.statement);
                    handleEvaluate(p.statement);
                  }}
                  className="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 active:bg-white/25 text-xs text-slate-200 border border-white/10 transition-colors cursor-pointer text-left flex items-center gap-1.5"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                  <span>{p.category}: {p.statement.slice(0, 48)}...</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 text-rose-700 dark:text-rose-300 text-sm">
          {error}
        </div>
      )}

      {/* Results Section */}
      {result && (
        <div className="space-y-6">
          {/* Dimension Classification Banner */}
          <div className="rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 shadow-sm">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Geanalyseerde Stelling:
                </span>
                <h3 className="text-lg font-bold text-slate-900 dark:text-white mt-0.5">
                  "{result.statement}"
                </h3>
              </div>

              {/* Dimension Badges */}
              <div className="flex flex-wrap items-center gap-2">
                <div className="px-3.5 py-1.5 rounded-lg bg-blue-50 dark:bg-blue-950/50 border border-blue-200 dark:border-blue-800 text-xs">
                  <span className="text-slate-500 dark:text-slate-400">Economisch: </span>
                  <span className="font-bold text-blue-700 dark:text-blue-300">{result.dimensions.lr_label}</span>
                </div>
                <div className="px-3.5 py-1.5 rounded-lg bg-purple-50 dark:bg-purple-950/50 border border-purple-200 dark:border-purple-800 text-xs">
                  <span className="text-slate-500 dark:text-slate-400">Maatschappelijk: </span>
                  <span className="font-bold text-purple-700 dark:text-purple-300">{result.dimensions.pc_label}</span>
                </div>
                {onViewOnCompass && (
                  <button
                    onClick={() => onViewOnCompass({
                      x: result.dimensions.left_right_orientation * 4,
                      y: result.dimensions.prog_cons_orientation * 4,
                      label: result.statement.slice(0, 40) + '...'
                    })}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 text-white dark:bg-white dark:text-slate-900 text-xs font-semibold hover:opacity-90 transition-opacity cursor-pointer"
                  >
                    <Compass className="w-3.5 h-3.5" />
                    Bekijk op Kieskompas
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Filter Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 dark:border-slate-800 pb-4">
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
              <span className="text-xs font-semibold text-slate-500 mr-2 flex items-center gap-1">
                <Filter className="w-3.5 h-3.5" /> Filter:
              </span>
              {[
                { key: 'all' as const, label: 'Alle Partijen', count: result.party_stances.length },
                { key: 'pro' as const, label: 'Voor (+)', count: result.party_stances.filter(p => p.score !== null && p.score >= 0.5).length },
                { key: 'neutral' as const, label: 'Neutraal (0)', count: result.party_stances.filter(p => p.score !== null && p.score > -0.5 && p.score < 0.5).length },
                { key: 'against' as const, label: 'Tegen (-)', count: result.party_stances.filter(p => p.score !== null && p.score <= -0.5).length },
                { key: 'unknown' as const, label: 'Niet vermeld (?)', count: result.party_stances.filter(p => p.is_unknown || p.score === null).length },
              ].map(f => (
                <button
                  key={f.key}
                  onClick={() => setFilterStance(f.key)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 cursor-pointer whitespace-nowrap ${
                    filterStance === f.key
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300'
                  }`}
                >
                  <span>{f.label}</span>
                  <span className={`px-1.5 py-0.2 rounded-full text-[10px] ${
                    filterStance === f.key ? 'bg-blue-700 text-blue-100' : 'bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300'
                  }`}>
                    {f.count}
                  </span>
                </button>
              ))}
            </div>

            <span className="text-xs text-slate-500 dark:text-slate-400">
              Toont <strong>{filteredParties.length}</strong> partijen
            </span>
          </div>

          {/* A-Z Party Cards List */}
          <div className="space-y-4">
            {filteredParties.map(ps => {
              const isExpanded = !!expandedQuotes[ps.party_id];
              const hasQuotes = ps.quotes && ps.quotes.length > 0;

              return (
                <div
                  key={ps.party_id}
                  className="rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 shadow-sm hover:border-slate-300 dark:hover:border-slate-700 transition-all"
                  style={{ borderLeftWidth: '5px', borderLeftColor: ps.party_color || '#0052cc' }}
                >
                  {/* Top Bar: Name + Score Badge */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 mb-2.5">
                    <div className="flex items-center gap-3">
                      <div
                        className="w-3.5 h-3.5 rounded-full shrink-0 shadow-sm"
                        style={{ backgroundColor: ps.party_color || '#0052cc' }}
                      />
                      <h4 className="text-base font-bold text-slate-900 dark:text-white">
                        {ps.party_name}
                      </h4>
                      <button
                        onClick={() => onSelectParty(ps.party_id)}
                        className="text-slate-400 hover:text-blue-600 transition-colors p-1"
                        title="Bekijk partij dossier"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                      </button>
                    </div>

                    <div>{getScoreBadge(ps)}</div>
                  </div>

                  {/* Stance Explanation */}
                  <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed mb-3">
                    {ps.explanation}
                  </p>

                  {/* Verified Quotes Section */}
                  {hasQuotes && (
                    <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-800/80">
                      <button
                        onClick={() => toggleQuotes(ps.party_id)}
                        className="flex items-center justify-between w-full text-xs font-semibold text-blue-600 dark:text-blue-400 hover:text-blue-700 transition-colors py-1 cursor-pointer"
                      >
                        <span className="flex items-center gap-1.5">
                          <BookOpen className="w-3.5 h-3.5" />
                          <span>
                            {isExpanded ? 'Verberg PDF passages' : `Bekijk ${ps.quotes.length} geverifieerde bronpassages uit het PDF programma`}
                          </span>
                        </span>
                        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                      </button>

                      {isExpanded && (
                        <div className="mt-3 space-y-2.5">
                          {ps.quotes.map((q, qIdx) => (
                            <div
                              key={qIdx}
                              className="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/80 text-xs"
                            >
                              <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-1.5">
                                <span className="font-semibold text-slate-700 dark:text-slate-300">
                                  📄 {q.filename}
                                </span>
                                <span className="px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-900/60 text-blue-700 dark:text-blue-300 font-bold">
                                  Pagina {q.page}
                                </span>
                              </div>
                              <blockquote className="italic text-slate-700 dark:text-slate-300 border-l-2 border-blue-400 pl-3 my-1 leading-relaxed">
                                "{q.text}"
                              </blockquote>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

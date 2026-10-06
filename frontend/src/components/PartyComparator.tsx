import React, { useState, useEffect } from 'react';
import { GitCompare, Check, Loader2, BookOpen } from 'lucide-react';
import { api } from '../api/client';
import type { PartySummary, ThemeInfo, CompareResponse } from '../types';

interface PartyComparatorProps {
  onSelectParty: (partyId: string) => void;
}

export const PartyComparator: React.FC<PartyComparatorProps> = ({ onSelectParty }) => {
  const [allParties, setAllParties] = useState<PartySummary[]>([]);
  const [themes, setThemes] = useState<ThemeInfo[]>([]);
  const [selectedPartyIds, setSelectedPartyIds] = useState<string[]>(['pvv', 'gl-pvda', 'vvd', 'nsc']);
  const [selectedThemeKeys, setSelectedThemeKeys] = useState<string[]>(['klimaat', 'wonen', 'zorg', 'migratie', 'economie', 'veiligheid']);
  const [comparison, setComparison] = useState<CompareResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    Promise.all([api.getParties(), api.getThemes()])
      .then(([partiesData, themesData]) => {
        setAllParties(partiesData);
        setThemes(themesData);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (selectedPartyIds.length === 0) {
      setComparison(null);
      return;
    }

    setIsLoading(true);
    api.compareParties(selectedPartyIds, selectedThemeKeys)
      .then(setComparison)
      .catch(() => {})
      .finally(() => setIsLoading(false));
  }, [selectedPartyIds, selectedThemeKeys]);

  const toggleParty = (id: string) => {
    if (selectedPartyIds.includes(id)) {
      if (selectedPartyIds.length > 1) {
        setSelectedPartyIds(selectedPartyIds.filter(pid => pid !== id));
      }
    } else {
      if (selectedPartyIds.length < 5) {
        setSelectedPartyIds([...selectedPartyIds, id]);
      }
    }
  };

  const toggleTheme = (key: string) => {
    if (selectedThemeKeys.includes(key)) {
      if (selectedThemeKeys.length > 1) {
        setSelectedThemeKeys(selectedThemeKeys.filter(k => k !== key));
      }
    } else {
      setSelectedThemeKeys([...selectedThemeKeys, key]);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300 text-xs font-semibold mb-2">
          <GitCompare className="w-3.5 h-3.5" />
          Thema Matrix Vergelijker
        </div>
        <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
          Zij-aan-Zij Standpunten Vergelijker
        </h2>
        <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
          Kies tot 5 partijen en vergelijk hun standpunten en geciteerde passages rechtstreeks op de belangrijkste verkiezingsthema's.
        </p>
      </div>

      {/* Selectors Panel */}
      <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        {/* Parties multi-select */}
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">
            Selecteer Partijen (Kies 2 tot 5):
          </span>
          <div className="flex flex-wrap gap-2">
            {allParties.slice(0, 15).map(p => {
              const isSelected = selectedPartyIds.includes(p.id);
              return (
                <button
                  key={p.id}
                  onClick={() => toggleParty(p.id)}
                  className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer shadow-xs ${
                    isSelected
                      ? 'text-white scale-102 ring-2 ring-blue-500/40'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200'
                  }`}
                  style={isSelected ? { backgroundColor: p.color } : {}}
                >
                  {isSelected && <Check className="w-3.5 h-3.5" />}
                  <span>{p.name}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Themes toggle */}
        <div className="pt-3 border-t border-slate-100 dark:border-slate-800">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">
            Thema's Insluiten:
          </span>
          <div className="flex flex-wrap gap-2">
            {themes.map(t => {
              const isSelected = selectedThemeKeys.includes(t.key);
              return (
                <button
                  key={t.key}
                  onClick={() => toggleTheme(t.key)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
                    isSelected
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200'
                  }`}
                >
                  {t.title}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="p-16 flex flex-col items-center justify-center gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          <p className="text-sm font-semibold text-slate-500">Standpunten naast elkaar leggen...</p>
        </div>
      )}

      {/* Comparison Matrix */}
      {comparison && !isLoading && (
        <div className="space-y-8">
          {comparison.themes.map(t => (
            <div
              key={t.theme_key}
              className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm"
            >
              {/* Theme Header */}
              <div className="bg-slate-50 dark:bg-slate-800/80 px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
                  <h3 className="text-lg font-extrabold text-slate-900 dark:text-white">
                    {t.theme_name}
                  </h3>
                </div>
                <span className="text-xs text-slate-400 font-medium">Thema Vergelijking</span>
              </div>

              {/* Side-by-side columns */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 divide-y md:divide-y-0 md:divide-x divide-slate-200 dark:divide-slate-800">
                {comparison.parties.map(p => {
                  const stance = t.stances[p.id];
                  return (
                    <div key={p.id} className="p-5 space-y-3 flex flex-col">
                      {/* Party Header */}
                      <div className="flex items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-2">
                        <div className="flex items-center gap-2">
                          <span
                            className="px-2 py-0.5 rounded text-[11px] font-black text-white"
                            style={{ backgroundColor: p.color }}
                          >
                            {p.name}
                          </span>
                          <span className="text-xs text-slate-500 font-medium truncate max-w-[120px]">
                            {p.leader}
                          </span>
                        </div>
                        <button
                          onClick={() => onSelectParty(p.id)}
                          className="text-[11px] text-blue-600 hover:underline font-semibold cursor-pointer shrink-0"
                        >
                          Dossier
                        </button>
                      </div>

                      {/* Stance content */}
                      {stance ? (
                        <>
                          <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed italic bg-slate-50 dark:bg-slate-800/50 p-3 rounded-xl border border-slate-100 dark:border-slate-800/60">
                            "{stance.summary}"
                          </p>

                          {stance.quotes && stance.quotes.length > 0 && (
                            <div className="mt-auto pt-2">
                              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1 mb-1">
                                <BookOpen className="w-3 h-3" /> Pagina {stance.quotes[0].page}:
                              </span>
                              <p className="text-[11px] text-slate-600 dark:text-slate-400 border-l border-blue-400 pl-2 leading-relaxed">
                                "{stance.quotes[0].text}"
                              </p>
                            </div>
                          )}
                        </>
                      ) : (
                        <p className="text-xs text-slate-400">Geen specifieke gegevens beschikbaar.</p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

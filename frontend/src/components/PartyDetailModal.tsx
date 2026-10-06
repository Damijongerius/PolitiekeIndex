import React, { useState, useEffect } from 'react';
import {
  X, Download, FileText, ChevronRight, ChevronLeft,
  BookOpen, Sparkles, Loader2, Building2, Users, Globe, ExternalLink
} from 'lucide-react';

import { api } from '../api/client';
import type { PartyDetail, ThemeDetail, Quote, Kamerlid } from '../types';


interface PartyDetailModalProps {
  partyId: string | null;
  onClose: () => void;
}

export const PartyDetailModal: React.FC<PartyDetailModalProps> = ({ partyId, onClose }) => {
  const [detail, setDetail] = useState<PartyDetail | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'visie' | 'themas' | 'pdf' | 'fractie'>('visie');

  const [selectedTheme, setSelectedTheme] = useState<string>('klimaat');

  // PDF Page Reader state
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageText, setPageText] = useState<string>('');
  const [isPageLoading, setIsPageLoading] = useState<boolean>(false);
  const [totalPages, setTotalPages] = useState<number>(1);

  useEffect(() => {
    if (!partyId) {
      setDetail(null);
      return;
    }

    setIsLoading(true);
    api.getPartyDetail(partyId)
      .then(res => {
        setDetail(res);
        setTotalPages(res.pageCount || 50);
        setCurrentPage(1);
      })
      .catch(err => {
        console.error(err);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [partyId]);

  // Load PDF page text when tab changes to 'pdf' or page number changes
  useEffect(() => {
    if (activeTab === 'pdf' && partyId) {
      setIsPageLoading(true);
      api.getPageText(partyId, currentPage)
        .then(res => {
          setPageText(res.text || 'Geen tekst gevonden op deze pagina.');
          if (res.totalPages) setTotalPages(res.totalPages);
        })
        .catch(() => {
          setPageText('Fout bij het inlezen van deze pagina.');
        })
        .finally(() => {
          setIsPageLoading(false);
        });
    }
  }, [activeTab, partyId, currentPage]);

  if (!partyId) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/70 backdrop-blur-sm flex items-center justify-center p-3 sm:p-6 animate-in fade-in duration-200">
      <div className="relative w-full max-w-4xl bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col max-h-[92vh]">
        {/* Loading state */}
        {isLoading && (
          <div className="p-16 flex flex-col items-center justify-center gap-3">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            <p className="text-sm font-semibold text-slate-500">Partij dossier inladen...</p>
          </div>
        )}

        {detail && !isLoading && (
          <>
            {/* Header with Party Color Banner */}
            <div
              className="p-6 text-white relative flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
              style={{ backgroundColor: detail.color }}
            >
              <button
                onClick={onClose}
                className="absolute top-4 right-4 p-2 rounded-full bg-black/20 hover:bg-black/40 text-white transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>

              <div className="flex items-center gap-4">
                {/* Party Cover Thumbnail */}
                <div className="w-16 h-22 rounded-lg bg-white/20 p-1 shadow-md shrink-0 overflow-hidden hidden sm:block">
                  <img
                    src={detail.coverUrl}
                    alt={detail.name}
                    className="w-full h-full object-cover rounded"
                    onError={(e) => {
                      (e.target as HTMLElement).style.display = 'none';
                    }}
                  />
                </div>

                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-extrabold uppercase px-2.5 py-0.5 rounded-full bg-white/20 text-white border border-white/30">
                      {detail.orientation}
                    </span>
                    {detail.inParliament && (
                      <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-white text-slate-900">
                        {detail.seats} zetels
                      </span>
                    )}
                  </div>
                  <h2 className="text-2xl sm:text-3xl font-black tracking-tight drop-shadow-sm">
                    {detail.fullName} ({detail.name})
                  </h2>
                  <p className="text-xs text-white/90 mt-0.5">
                    Lijsttrekker / Partijleider: <strong>{detail.leader}</strong>
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2 self-stretch sm:self-auto">
                <a
                  href={detail.pdfUrl}
                  download
                  className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-white text-slate-900 font-bold text-xs shadow-md hover:bg-slate-100 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  <span>Download PDF</span>
                </a>
              </div>
            </div>

            {/* Navigation Tabs */}
            <div className="flex border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 px-6">
              {[
                { id: 'visie' as const, label: 'Kernvisie & Profiel' },
                { id: 'themas' as const, label: 'Thema Standpunten (6)' },
                { id: 'fractie' as const, label: `Kamerleden & Fractie (${detail.seats})` },
                { id: 'pdf' as const, label: 'PDF Document Bladeren' },
              ].map(t => (

                <button
                  key={t.id}
                  onClick={() => setActiveTab(t.id)}
                  className={`py-3.5 px-4 text-xs sm:text-sm font-semibold border-b-2 transition-colors cursor-pointer ${
                    activeTab === t.id
                      ? 'border-blue-600 text-blue-600 dark:text-blue-400 bg-white dark:bg-slate-900'
                      : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {/* Tab Contents Container */}
            <div className="p-6 overflow-y-auto flex-1 space-y-6">
              {/* TAB 1: VISIE */}
              {activeTab === 'visie' && (
                <div className="space-y-6">
                  {/* Vision Quote Card */}
                  <div className="p-5 rounded-2xl bg-blue-50/60 dark:bg-blue-950/40 border border-blue-200/80 dark:border-blue-800/80">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-blue-800 dark:text-blue-300 mb-2 flex items-center gap-2">
                      <Sparkles className="w-4 h-4" /> Kernvisie uit het Verkiezingsprogramma
                    </h4>
                    <p className="text-sm sm:text-base text-slate-800 dark:text-slate-200 leading-relaxed italic">
                      "{detail.visionSummary}"
                    </p>
                  </div>

                  {/* Core Attributes */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 text-center">
                      <span className="text-xs text-slate-500 dark:text-slate-400 block mb-1">Tweede Kamer Zetels</span>
                      <strong className="text-2xl font-black text-slate-900 dark:text-white">{detail.seats}</strong>
                    </div>
                    <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 text-center">
                      <span className="text-xs text-slate-500 dark:text-slate-400 block mb-1">Economische Positie</span>
                      <strong className="text-base font-bold text-slate-900 dark:text-white">
                        {detail.compass.x > 0 ? `+${detail.compass.x} Rechts` : detail.compass.x < 0 ? `${detail.compass.x} Links` : 'Centrum'}
                      </strong>
                    </div>
                    <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 text-center">
                      <span className="text-xs text-slate-500 dark:text-slate-400 block mb-1">Maatschappelijke Positie</span>
                      <strong className="text-base font-bold text-slate-900 dark:text-white">
                        {detail.compass.y > 0 ? `+${detail.compass.y} Progressief` : detail.compass.y < 0 ? `${detail.compass.y} Conservatief` : 'Midden'}
                      </strong>
                    </div>
                  </div>

                  {/* Program Details */}
                  <div className="p-5 rounded-2xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white mb-2">
                      Over het verkiezingsprogramma
                    </h4>
                    <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                      {detail.shortDescription}
                    </p>
                    {detail.pageCount && (
                      <p className="text-xs text-slate-400 mt-3 flex items-center gap-1.5">
                        <FileText className="w-3.5 h-3.5" /> Het officiële PDF document beslaat <strong>{detail.pageCount} pagina's</strong>.
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* TAB 2: THEMAS */}
              {activeTab === 'themas' && (
                <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
                  {/* Theme Selector list */}
                  <div className="md:col-span-4 space-y-1.5">
                    {Object.entries(detail.themes).map(([key, tDetail]) => (
                      <button
                        key={key}
                        onClick={() => setSelectedTheme(key)}
                        className={`w-full text-left px-3.5 py-3 rounded-xl text-xs sm:text-sm font-semibold transition-all flex items-center justify-between cursor-pointer ${
                          selectedTheme === key
                            ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/20'
                            : 'bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300'
                        }`}
                      >
                        <span>{(tDetail as ThemeDetail).title}</span>
                        <ChevronRight className="w-4 h-4 opacity-70" />
                      </button>
                    ))}

                  </div>

                  {/* Theme Details View */}
                  <div className="md:col-span-8">
                    {detail.themes[selectedTheme] ? (
                      (() => {
                        const curTheme = detail.themes[selectedTheme];
                        return (
                          <div className="rounded-2xl border border-slate-200 dark:border-slate-800 p-5 bg-white dark:bg-slate-900 shadow-sm space-y-4">
                            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                              <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                                {curTheme.title}
                              </h3>
                              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300">
                                {curTheme.label}
                              </span>
                            </div>

                            <div>
                              <h5 className="text-xs font-bold uppercase text-slate-400 mb-1.5">Standpunt Samenvatting</h5>
                              <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/60 p-4 rounded-xl border border-slate-100 dark:border-slate-800">
                                {curTheme.summary}
                              </p>
                            </div>

                            {curTheme.quotes && curTheme.quotes.length > 0 && (
                              <div>
                                <h5 className="text-xs font-bold uppercase text-slate-400 mb-2 flex items-center gap-1.5">
                                  <BookOpen className="w-3.5 h-3.5" /> Geciteerde PDF Passages:
                                </h5>
                                <div className="space-y-2">
                                  {curTheme.quotes.map((q: Quote, idx: number) => (
                                    <div
                                      key={idx}
                                      className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-xs"
                                    >

                                      <div className="flex items-center justify-between text-slate-500 mb-1 font-semibold">
                                        <span>Pagina {q.page}</span>
                                        <span>{q.filename}</span>
                                      </div>
                                      <p className="italic text-slate-700 dark:text-slate-300 border-l-2 border-blue-500 pl-2.5 my-1">
                                        "{q.text}"
                                      </p>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        );
                      })()
                    ) : (
                      <p className="text-sm text-slate-400">Selecteer een thema om de details te zien.</p>
                    )}
                  </div>
                </div>
              )}

              {/* TAB 3: FRACTIE & KAMERLEDEN */}
              {activeTab === 'fractie' && (
                <div className="space-y-6">
                  {detail.tkData ? (
                    <>
                      {/* Fractie Banner */}
                      <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                        <div className="flex items-center gap-4">
                          {detail.tkData.logo && (
                            <img
                              src={detail.tkData.logo}
                              alt={detail.tkData.name}
                              className="h-10 max-w-[120px] object-contain"
                              onError={(e) => { (e.target as HTMLElement).style.display = 'none'; }}
                            />
                          )}
                          <div>
                            <span className="text-xs font-bold text-blue-600 dark:text-blue-400 block uppercase tracking-wider">
                              Officiële Tweede Kamer Fractie
                            </span>
                            <h4 className="text-lg font-bold text-slate-900 dark:text-white">
                              {detail.tkData.name}
                            </h4>
                            <p className="text-xs text-slate-500">
                              {detail.tkData.seats} {detail.tkData.seats === 1 ? 'zetel' : 'zetels'} in het parlement
                            </p>
                          </div>
                        </div>

                        {/* Contact Buttons */}
                        <div className="flex flex-wrap items-center gap-2">
                          {detail.tkData.website && (
                            <a
                              href={detail.tkData.website}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 hover:bg-slate-100 text-xs font-semibold text-slate-700 dark:text-slate-200"
                            >
                              <Globe className="w-3.5 h-3.5 text-blue-500" />
                              Website
                              <ExternalLink className="w-3 h-3 opacity-60" />
                            </a>
                          )}
                          {detail.tkData.detailUrl && (
                            <a
                              href={detail.tkData.detailUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 hover:bg-blue-100 text-xs font-semibold text-blue-700 dark:text-blue-300"
                            >
                              <Building2 className="w-3.5 h-3.5 text-blue-600" />
                              Tweedekamer.nl
                              <ExternalLink className="w-3 h-3 opacity-60" />
                            </a>
                          )}
                        </div>
                      </div>

                      {/* Fractievoorzitter */}
                      {detail.tkData.leader && (
                        <div className="p-4 rounded-xl bg-blue-50/60 dark:bg-blue-950/40 border border-blue-100 dark:border-blue-900 flex items-center gap-4">
                          {detail.tkData.leaderPhoto ? (
                            <img
                              src={detail.tkData.leaderPhoto}
                              alt={detail.tkData.leader}
                              className="w-14 h-14 rounded-full object-cover border-2 border-white dark:border-slate-800 shadow"
                            />
                          ) : (
                            <div className="w-14 h-14 rounded-full bg-blue-200 dark:bg-blue-800 flex items-center justify-center font-bold text-blue-900 dark:text-blue-100 text-lg">
                              {detail.tkData.leader.charAt(0)}
                            </div>
                          )}
                          <div>
                            <span className="text-xs font-bold text-blue-700 dark:text-blue-300 uppercase tracking-wider block">
                              {detail.tkData.leaderRole || 'Fractievoorzitter'}
                            </span>
                            <h5 className="text-base font-extrabold text-slate-900 dark:text-white">
                              {detail.tkData.leader}
                            </h5>
                            <p className="text-xs text-slate-600 dark:text-slate-400">
                              Leidt de {detail.tkData.name}-fractie in de Tweede Kamer
                            </p>
                          </div>
                        </div>
                      )}

                      {/* Members Grid */}
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <Users className="w-4 h-4 text-blue-600" />
                            Kamerleden van deze fractie ({detail.tkData.members.length})
                          </h4>
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                          {detail.tkData.members.map((m: Kamerlid, idx: number) => (
                            <div
                              key={idx}
                              className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 flex items-center gap-3"
                            >
                              {m.photo ? (
                                <img
                                  src={m.photo}
                                  alt={m.name}
                                  className="w-10 h-10 rounded-full object-cover shrink-0 border border-slate-200 dark:border-slate-700"
                                />
                              ) : (
                                <div className="w-10 h-10 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center font-bold text-slate-600 shrink-0">
                                  {m.name.charAt(0)}
                                </div>
                              )}
                              <div className="min-w-0 flex-1">
                                {m.link ? (
                                  <a
                                    href={m.link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-xs font-bold text-slate-900 dark:text-white hover:text-blue-600 truncate block"
                                  >
                                    {m.name}
                                  </a>
                                ) : (
                                  <span className="text-xs font-bold text-slate-900 dark:text-white truncate block">
                                    {m.name}
                                  </span>
                                )}
                                <span className="text-[10px] text-slate-400 block truncate">{m.role}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="p-8 text-center rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-2">
                      <Users className="w-8 h-8 mx-auto text-slate-400" />
                      <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200">
                        Buitenparlementaire Partij
                      </h4>
                      <p className="text-xs text-slate-500 max-w-sm mx-auto">
                        {detail.name} heeft momenteel geen zetels in de Tweede Kamer der Staten-Generaal.
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* TAB 4: PDF PAGE BROWSER */}
              {activeTab === 'pdf' && (

                <div className="space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                    <div>
                      <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                        Doorzoek de originele PDF tekst
                      </h4>
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        Geëxtraheerd met pdfplumber • Totaal {totalPages} pagina's
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setCurrentPage((p: number) => Math.max(1, p - 1))}
                        disabled={currentPage <= 1 || isPageLoading}
                        className="p-2 rounded-lg bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 disabled:opacity-40 cursor-pointer"
                      >
                        <ChevronLeft className="w-4 h-4" />
                      </button>
                      <span className="text-xs font-bold text-slate-700 dark:text-slate-300 px-2">
                        Pagina {currentPage} / {totalPages}
                      </span>
                      <button
                        onClick={() => setCurrentPage((p: number) => Math.min(totalPages, p + 1))}
                        disabled={currentPage >= totalPages || isPageLoading}
                        className="p-2 rounded-lg bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 disabled:opacity-40 cursor-pointer"
                      >
                        <ChevronRight className="w-4 h-4" />
                      </button>

                    </div>
                  </div>

                  {/* Page Text Area */}
                  <div className="relative rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 p-5 min-h-[300px] shadow-inner font-mono text-xs leading-relaxed text-slate-800 dark:text-slate-200 whitespace-pre-wrap overflow-y-auto max-h-[400px]">
                    {isPageLoading ? (
                      <div className="absolute inset-0 flex items-center justify-center bg-white/60 dark:bg-slate-950/60 backdrop-blur-xs">
                        <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
                      </div>
                    ) : (
                      pageText
                    )}
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

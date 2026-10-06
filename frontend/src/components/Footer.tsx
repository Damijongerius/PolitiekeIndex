import React from 'react';
import { Database, Sparkles, BookOpen } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="mt-20 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 py-10 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🇳🇱</span>
            <div>
              <p className="text-sm font-extrabold text-slate-900 dark:text-white">
                PolitiekKompas NL
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Onafhankelijke data-analyse van Nederlandse politieke standpunten & verkiezingsprogramma's
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-4 text-xs text-slate-500 dark:text-slate-400">
            <span className="flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5 text-blue-500" />
              ChromaDB Vector Store
            </span>
            <span>•</span>
            <span className="flex items-center gap-1.5">
              <BookOpen className="w-3.5 h-3.5 text-emerald-500" />
              pdfplumber extractie
            </span>
            <span>•</span>
            <span className="flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-purple-500" />
              FastAPI + React TypeScript
            </span>
          </div>
        </div>

        <div className="mt-6 pt-6 border-t border-slate-100 dark:border-slate-800/80 text-center text-xs text-slate-400">
          Alle getoonde citaten en paginanummers zijn afkomstig uit de officiële verkiezingsprogramma's voor de Tweede Kamer.
        </div>
      </div>
    </footer>
  );
};

import { useState } from 'react';
import { Navbar, type NavTab } from './components/Navbar';
import { StellingChecker } from './components/StellingChecker';
import { PoliticalCompass } from './components/PoliticalCompass';
import { PartyDirectory } from './components/PartyDirectory';
import { PartyComparator } from './components/PartyComparator';
import { TweedeKamerFracties } from './components/TweedeKamerFracties';
import { PartyDetailModal } from './components/PartyDetailModal';

import { Footer } from './components/Footer';

export function App() {
  const [activeTab, setActiveTab] = useState<NavTab>('stellingen');
  const [selectedPartyId, setSelectedPartyId] = useState<string | null>(null);
  const [compassPoint, setCompassPoint] = useState<{ x: number; y: number; label: string } | null>(null);

  const handleSelectParty = (partyId: string) => {
    setSelectedPartyId(partyId);
  };

  const handleViewOnCompass = (point: { x: number; y: number; label: string }) => {
    setCompassPoint(point);
    setActiveTab('kompas');
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors">
      {/* Top Navigation */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6 sm:pt-8 pb-12">
        {activeTab === 'stellingen' && (
          <StellingChecker
            onSelectParty={handleSelectParty}
            onViewOnCompass={handleViewOnCompass}
          />
        )}

        {activeTab === 'kompas' && (
          <PoliticalCompass
            onSelectParty={handleSelectParty}
            userStatementPoint={compassPoint}
          />
        )}

        {activeTab === 'fracties' && (
          <TweedeKamerFracties onSelectParty={handleSelectParty} />
        )}

        {activeTab === 'partijen' && (
          <PartyDirectory onSelectParty={handleSelectParty} />
        )}


        {activeTab === 'vergelijker' && (
          <PartyComparator onSelectParty={handleSelectParty} />
        )}
      </main>

      {/* Party Dossier Detail Modal */}
      <PartyDetailModal
        partyId={selectedPartyId}
        onClose={() => setSelectedPartyId(null)}
      />

      {/* Site Footer */}
      <Footer />
    </div>
  );
}

export default App;

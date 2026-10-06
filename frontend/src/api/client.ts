import type {
  PartySummary, PartyDetail, StatementEvaluationResponse,
  CompassResponse, PresetStatement, ThemeInfo, CompareResponse,
  TweedeKamerResponse
} from '../types';


const BASE_URL = '/api';

export const api = {
  async getHealth(): Promise<{ status: string; parties_indexed: number; themes_count: number; db_chunks_count: number }> {
    const res = await fetch(`${BASE_URL}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return res.json();
  },

  async getPresets(): Promise<PresetStatement[]> {
    const res = await fetch(`${BASE_URL}/presets`);
    if (!res.ok) throw new Error('Failed to load presets');
    return res.json();
  },

  async getThemes(): Promise<ThemeInfo[]> {
    const res = await fetch(`${BASE_URL}/themes`);
    if (!res.ok) throw new Error('Failed to load themes');
    return res.json();
  },

  async getParties(): Promise<PartySummary[]> {
    const res = await fetch(`${BASE_URL}/parties`);
    if (!res.ok) throw new Error('Failed to load parties');
    return res.json();
  },

  async getPartyDetail(partyId: string): Promise<PartyDetail> {
    const res = await fetch(`${BASE_URL}/parties/${partyId}`);
    if (!res.ok) throw new Error(`Failed to load party ${partyId}`);
    return res.json();
  },

  async evaluateStatement(statement: string): Promise<StatementEvaluationResponse> {
    const res = await fetch(`${BASE_URL}/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ statement }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Evaluation failed' }));
      throw new Error(err.detail || 'Evaluation failed');
    }
    return res.json();
  },

  async getCompass(): Promise<CompassResponse> {
    const res = await fetch(`${BASE_URL}/compass`);
    if (!res.ok) throw new Error('Failed to load compass data');
    return res.json();
  },

  async compareParties(partyIds: string[], themeKeys?: string[]): Promise<CompareResponse> {
    const res = await fetch(`${BASE_URL}/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ party_ids: partyIds, theme_keys: themeKeys }),
    });
    if (!res.ok) throw new Error('Failed to compare parties');
    return res.json();
  },

  async getPageText(partyId: string, pageNum: number): Promise<{ party_id: string; page: number; totalPages: number; text: string }> {
    const res = await fetch(`${BASE_URL}/parties/${partyId}/pages/${pageNum}`);
    if (!res.ok) throw new Error(`Failed to load page ${pageNum}`);
    return res.json();
  },

  async getTweedeKamerFracties(refresh = false): Promise<TweedeKamerResponse> {
    const res = await fetch(`${BASE_URL}/tweedekamer/fracties${refresh ? '?refresh=true' : ''}`);
    if (!res.ok) throw new Error('Failed to load Tweede Kamer fracties');
    return res.json();
  },

  async triggerScrape(): Promise<TweedeKamerResponse> {
    const res = await fetch(`${BASE_URL}/tweedekamer/scrape`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to trigger Tweede Kamer scrape');
    return res.json();
  },
};


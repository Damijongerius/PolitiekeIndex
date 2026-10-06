export interface Quote {
  page: number;
  filename: string;
  text: string;
}

export interface PartyStance {
  party_id: string;
  party_name: string;
  party_color: string;
  score: number | null;
  score_label: string;
  is_unknown: boolean;
  explanation: string;
  quotes: Quote[];
}

export interface Dimensions {
  statement: string;
  left_right_orientation: number;
  prog_cons_orientation: number;
  lr_label: string;
  pc_label: string;
  economic_explanation?: string;
  cultural_explanation?: string;
}

export interface StatementEvaluationResponse {
  statement: string;
  dimensions: Dimensions;
  party_stances: PartyStance[];
}

export interface CompassParty {
  id: string;
  name: string;
  fullName: string;
  color: string;
  textColor: string;
  x: number;
  y: number;
  seats: number;
  inParliament: boolean;
  summary: string;
}

export interface CompassResponse {
  parties: CompassParty[];
  user_statement_point?: { x: number; y: number; label: string };
}

export interface ThemeDetail {
  title: string;
  score: number;
  label: string;
  summary: string;
  quotes: Quote[];
}

export interface Kamerlid {
  name: string;
  role: string;
  link?: string | null;
  photo?: string | null;
}

export interface FractieInfo {
  id: string;
  name: string;
  seats: number;
  leader?: string | null;
  leaderRole?: string | null;
  leaderPhoto?: string | null;
  logo?: string | null;
  detailUrl: string;
  fullTitle?: string | null;
  website?: string | null;
  email?: string | null;
  phone?: string | null;
  members: Kamerlid[];
  totalMembers?: number;
}

export interface TweedeKamerResponse {
  lastUpdated: string;
  sourceUrl: string;
  totalSeats: number;
  fractiesCount: number;
  fracties: FractieInfo[];
}

export interface PartySummary {
  id: string;
  name: string;
  fullName: string;
  leader: string;
  seats: number;
  inParliament: boolean;
  orientation: string;
  color: string;
  textColor: string;
  pdfAvailable: boolean;
  coverUrl: string;
  pdfUrl: string;
  pageCount?: number | null;
  compass: { x: number; y: number };
  shortDescription: string;
  tkData?: FractieInfo | null;
}

export interface PartyDetail extends PartySummary {
  visionSummary: string;
  themes: Record<string, ThemeDetail>;
}


export interface PresetStatement {
  id: string;
  category: string;
  statement: string;
  icon: string;
}

export interface ThemeInfo {
  key: string;
  title: string;
  icon: string;
  description: string;
  keywords: string[];
}

export interface ThemeComparisonItem {
  theme_key: string;
  theme_name: string;
  stances: Record<string, ThemeDetail>;
}

export interface CompareResponse {
  parties: PartySummary[];
  themes: ThemeComparisonItem[];
}

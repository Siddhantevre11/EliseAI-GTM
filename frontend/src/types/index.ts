export interface Lead {
  name: string;
  email: string;
  company: string;
  property_address: string;
  city: string;
  state: string;
}

export interface KeyDataPoints {
  renter_pct: number | null;
  vacancy_rate: number | null;
  rent_growth_pct: number | null;
  median_income: number | null;
  total_renter_units: number | null;
  top_news_headline: string | null;
  company_summary: string | null;
  walkscore: number | null;
  transitscore: number | null;
  bikescore: number | null;
  walkscore_description: string | null;
  data_source: string | null;
  is_fallback: boolean | null;
  rent_growth_is_fallback: boolean | null;
}

export interface Validation {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
  score: number;
  quality_grade: string;
}

export interface EmailDraft {
  subject: string;
  body: string;
}

export interface BuyingSignals {
  expansion_detected: boolean;
  expansion_detail: string | null;
  funding_detected: boolean;
  funding_detail: string | null;
  leadership_change: boolean;
  leadership_detail: string | null;
  portfolio_growth: boolean;
  portfolio_detail: string | null;
}

export interface ObjectionHandling {
  has_yardi?: string;
  too_expensive?: string;
  have_team?: string;
  not_priority?: string;
  current_solution?: string;
}

export interface PeerCaseStudy {
  similar_company: string;
  company_size: string;
  market: string;
  challenge: string;
  result: string;
}

export interface ROIEstimate {
  prospect_units: number;
  inquiries_per_month_est: number;
  avg_inquiry_handling_min: number;
  time_saved_hours_month: number;
  staff_cost_per_hour: number;
  monthly_savings: number;
  eliseai_cost_monthly: number;
  net_monthly_roi: number;
  annual_savings: number;
}

export interface DecisionMakerContext {
  company_size_tier: "National" | "Regional" | "Local";
  typical_buyer: string;
  primary_pain_point: string;
  what_they_google: string;
}

export interface IndustryBenchmark {
  avg_response_time_hours: number;
  prospect_response_time: number;
  avg_vacancy_rate: number;
  prospect_market_vacancy: number;
  avg_rent_growth: number;
  prospect_market_rent_growth: number;
}

export interface EnrichmentResult {
  tier: "A" | "B" | "C" | null;
  priority_score: number;
  score_rationale: string;
  key_data_points: KeyDataPoints;
  sales_signal: string;
  talking_points: string[];
  email_draft: EmailDraft | string;
  buying_signals: BuyingSignals;
  objection_handling: ObjectionHandling;
  peer_case_study: PeerCaseStudy;
  roi_estimate: ROIEstimate;
  decision_maker_context: DecisionMakerContext;
  industry_benchmark: IndustryBenchmark;
  estimated_time_saved_minutes: number;

  _lead?: Lead;
  _raw_data?: Record<string, unknown>;
  _api_errors?: string[];
  _needs_manual_review?: boolean;
  _clean_signal?: string;
  _strategy?: string;
  _apis_used?: string[];
  _enrichment_quality?: string;
  _validation?: Validation;
  error?: string;
}

export interface BatchStatus {
  total: number;
  processed: number;
  tierA: number;
  tierB: number;
  tierC: number;
  errors: number;
  currentLead?: string;
}
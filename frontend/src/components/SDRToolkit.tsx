"use client";

import { X, Copy, Send, ExternalLink, Zap, TrendingUp, Building2, Target, DollarSign, BarChart3, Shield, Briefcase, MessageSquare, TrendingDown } from "lucide-react";
import { EnrichmentResult } from "@/types";

interface SDRToolkitProps {
  isOpen: boolean;
  onClose: () => void;
  result: EnrichmentResult | null;
  onResendToSlack?: () => void;
  onCopyEmail?: () => void;
  onExportToSheets?: () => void;
}

function getTierBadge(tier: string): { bg: string; text: string; label: string } {
  const styles: Record<string, { bg: string; text: string; label: string }> = {
    A: { bg: "bg-emerald-500/10 border-emerald-500/20", text: "text-emerald-400", label: "Tier A" },
    B: { bg: "bg-amber-500/10 border-amber-500/20", text: "text-amber-400", label: "Tier B" },
    C: { bg: "bg-zinc-500/10 border-zinc-500/20", text: "text-zinc-400", label: "Tier C" },
    NEEDS_REVIEW: { bg: "bg-zinc-500/10 border-zinc-500/20", text: "text-zinc-400", label: "Needs Review" },
  };
  return styles[tier] || styles.C;
}

export function SDRToolkit({ isOpen, onClose, result, onResendToSlack, onCopyEmail, onExportToSheets }: SDRToolkitProps) {
  if (!isOpen || !result) return null;

  const lead = result._lead || ({} as any);
  const kdp = result.key_data_points || {};
  const email = result.email_draft as { subject?: string; body?: string } | string || { subject: "", body: "" };
  const emailSubject = typeof email === "string" ? "" : (email.subject || "");
  const emailBody = typeof email === "string" ? email : (email.body || "");
  const buying = result.buying_signals || {};
  const talkingPoints = result.talking_points || [];
  const salesSignal = result.sales_signal || "";
  const scoreRationale = result.score_rationale || "";
  const marketSignals = result.market_signals || [];
  const peerCaseStudy = result.peer_case_study || {};
  const roiEstimate = result.roi_estimate || {};
  const industryBenchmark = result.industry_benchmark || {};
  const decisionMaker = result.decision_maker_context || {};
  const objectionHandling = result.objection_handling || {};
  const tierBadge = getTierBadge((result.tier as string) || "C");
  const walkscore = kdp.walkscore;
  const tier = result.tier as string;

  // Color helpers - green for good metrics
  const vacancy = kdp.vacancy_rate || 0;
  const getVacancyColor = (v: number) => v < 5 ? 'text-emerald-400' : v < 8 ? 'text-amber-400' : 'text-red-400';

  const rentGrowth = kdp.rent_growth_pct ?? 0;
  const getRentGrowthColor = (v: number) => v > 0 ? 'text-emerald-400' : v === 0 ? 'text-zinc-400' : 'text-red-400';

  const renterPct = kdp.renter_pct || 0;
  const getRenterColor = (v: number) => v > 40 ? 'text-emerald-400' : v > 30 ? 'text-amber-400' : 'text-zinc-400';

  const score = result.priority_score || 0;
  const getScoreColor = (s: number) => s >= 75 ? 'text-emerald-400' : s >= 50 ? 'text-amber-400' : 'text-zinc-400';

  return (
    <div className="fixed right-0 top-14 z-40 flex h-[calc(100vh-56px)] w-[400px] flex-col border-l border-zinc-800 bg-zinc-900 shadow-xl">
      <div className="flex items-center justify-between border-b border-zinc-800 px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600">
            <Zap className="h-4 w-4 text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-zinc-50">SDR Toolkit</h2>
            <p className="text-xs text-zinc-500">
              {lead.company} - {lead.city}, {lead.state}
            </p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="rounded-lg p-2 text-zinc-500 hover:bg-zinc-800 hover:text-zinc-300"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <div className="flex-1 overflow-auto p-4 space-y-4">
        {/* Tier / Metrics Grid */}
        <div className="grid grid-cols-4 gap-2">
          <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-2">
            <div className="mb-0.5 text-[10px] text-zinc-500">Tier</div>
            <span className={`inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium ${tierBadge.bg} ${tierBadge.text}`}>
              {tierBadge.label}
            </span>
          </div>
          <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-2">
            <div className="mb-0.5 text-[10px] text-zinc-500">Score</div>
            <div className={`font-mono text-lg font-bold ${getScoreColor(score)}`}>{result.priority_score || 0}</div>
          </div>
          <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-2">
            <div className="mb-0.5 text-[10px] text-zinc-500">Renter %</div>
            <div className={`font-mono text-lg font-bold ${getRenterColor(renterPct)}`}>{kdp.renter_pct || 0}%</div>
          </div>
          <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-2">
            <div className="mb-0.5 text-[10px] text-zinc-500">Vacancy</div>
            <div className={`font-mono text-lg font-bold ${getVacancyColor(vacancy)}`}>{kdp.vacancy_rate || 0}%</div>
          </div>
        </div>

        {/* WalkScore & Income Row */}
        <div className="grid grid-cols-3 gap-2">
          {walkscore != null && walkscore > 0 && (
            <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-2">
              <div className="mb-0.5 text-[10px] text-zinc-500">WalkScore</div>
              <div className={`font-mono text-lg font-bold ${
                walkscore >= 70 ? 'text-emerald-400' : walkscore >= 50 ? 'text-amber-400' : 'text-zinc-400'
              }`}>{walkscore}</div>
            </div>
          )}
          {kdp.median_income != null && kdp.median_income > 0 && (
            <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-2">
              <div className="mb-0.5 text-[10px] text-zinc-500">Median Income</div>
              <div className="font-mono text-lg font-bold text-zinc-100">${(kdp.median_income / 1000).toFixed(0)}k</div>
            </div>
          )}
          {kdp.rent_growth_pct != null && (
            <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-2">
              <div className="mb-0.5 text-[10px] text-zinc-500">Rent Growth</div>
              <div className={`font-mono text-lg font-bold ${getRentGrowthColor(rentGrowth)}`}>
                {rentGrowth > 0 ? '+' : ''}{rentGrowth}%
              </div>
            </div>
          )}
        </div>

        {/* Sales Signal */}
        {salesSignal && (
          <div className="rounded-lg border border-zinc-800 bg-zinc-900/50">
            <div className="flex items-center gap-2 border-b border-zinc-800 bg-zinc-900/50 px-3 py-1.5">
              <Target className="h-3.5 w-3.5 text-zinc-500" />
              <h3 className="text-xs font-medium text-zinc-300">Sales Signal</h3>
            </div>
            <p className="p-2 font-mono text-xs text-zinc-400">{salesSignal}</p>
          </div>
        )}

        {/* Market Insights */}
        {marketSignals.length > 0 && (
          <div className="rounded-lg border border-zinc-800">
            <div className="flex items-center gap-2 border-b border-zinc-800 bg-zinc-900/50 px-3 py-1.5">
              <BarChart3 className="h-3.5 w-3.5 text-zinc-500" />
              <h3 className="text-xs font-medium text-zinc-300">Market Insights</h3>
            </div>
            <div className="space-y-1 p-2">
              {marketSignals.map((signal, i) => (
                <div key={i} className="flex items-start gap-2 text-xs">
                  <span className="mt-1 h-1.5 w-1.5 rounded-full bg-zinc-600"></span>
                  <span className="text-zinc-400">{signal}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* AI Research */}
        {scoreRationale && (
          <div className="rounded-lg border border-zinc-800">
            <div className="flex items-center gap-2 border-b border-zinc-800 bg-zinc-900/50 px-3 py-1.5">
              <Building2 className="h-3.5 w-3.5 text-zinc-500" />
              <h3 className="text-xs font-medium text-zinc-300">AI Research</h3>
            </div>
            <p className="p-2 text-xs text-zinc-400">{scoreRationale}</p>
          </div>
        )}

        {/* Company News */}
        {kdp.company_summary && (
          <div className="rounded-lg border border-zinc-800">
            <div className="flex items-center gap-2 border-b border-zinc-800 bg-zinc-900/50 px-3 py-1.5">
              <MessageSquare className="h-3.5 w-3.5 text-zinc-500" />
              <h3 className="text-xs font-medium text-zinc-300">Company Overview</h3>
            </div>
            <p className="p-2 text-xs text-zinc-400">{kdp.company_summary}</p>
          </div>
        )}

        {/* Top News Headline */}
        {kdp.top_news_headline && (
          <div className="rounded-lg border border-zinc-800">
            <div className="flex items-center gap-2 border-b border-zinc-800 bg-zinc-900/50 px-3 py-1.5">
              <TrendingUp className="h-3.5 w-3.5 text-zinc-500" />
              <h3 className="text-xs font-medium text-zinc-300">Latest News</h3>
            </div>
            <p className="p-2 text-xs text-zinc-400">{kdp.top_news_headline}</p>
          </div>
        )}

        {/* Peer Case Study */}
        {peerCaseStudy.similar_company && (
          <div className="rounded-lg border border-zinc-800">
            <div className="flex items-center gap-2 border-b border-zinc-800 bg-zinc-900/50 px-3 py-1.5">
              <Briefcase className="h-3.5 w-3.5 text-zinc-500" />
              <h3 className="text-xs font-medium text-zinc-300">Peer Success Story</h3>
            </div>
            <div className="space-y-2 p-2">
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-zinc-500">Company:</span>
                  <span className="ml-1 text-zinc-300">{peerCaseStudy.similar_company}</span>
                </div>
                <div>
                  <span className="text-zinc-500">Size:</span>
                  <span className="ml-1 text-zinc-300">{peerCaseStudy.company_size}</span>
                </div>
                <div>
                  <span className="text-zinc-500">Market:</span>
                  <span className="ml-1 text-zinc-300">{peerCaseStudy.market}</span>
                </div>
              </div>
              {peerCaseStudy.challenge && (
                <div className="pt-1 border-t border-zinc-800">
                  <p className="text-[10px] text-zinc-500 mb-1">Challenge</p>
                  <p className="text-xs text-zinc-400">{peerCaseStudy.challenge}</p>
                </div>
              )}
              {peerCaseStudy.result && (
                <div>
                  <p className="text-[10px] text-zinc-500 mb-1">Result</p>
                  <p className="text-xs text-emerald-400">{peerCaseStudy.result}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Industry Benchmark */}
        {industryBenchmark && (
          <div className="rounded-lg border border-zinc-800">
            <div className="flex items-center gap-2 border-b border-zinc-800 bg-zinc-900/50 px-3 py-1.5">
              <TrendingUp className="h-3.5 w-3.5 text-zinc-500" />
              <h3 className="text-xs font-medium text-zinc-300">Market Comparison</h3>
            </div>
            <div className="grid grid-cols-2 gap-2 p-2">
              {industryBenchmark.prospect_market_vacancy != null && (
                <div>
                  <p className="text-[10px] text-zinc-500">Market Vacancy</p>
                  <p className="font-mono text-sm text-zinc-300">{industryBenchmark.prospect_market_vacancy}%</p>
                </div>
              )}
              {industryBenchmark.prospect_market_rent_growth != null && (
                <div>
                  <p className="text-[10px] text-zinc-500">Rent Growth YoY</p>
                  <p className={`font-mono text-sm ${industryBenchmark.prospect_market_rent_growth >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {industryBenchmark.prospect_market_rent_growth > 0 ? '+' : ''}{industryBenchmark.prospect_market_rent_growth}%
                  </p>
                </div>
              )}
              {industryBenchmark.avg_vacancy_rate != null && industryBenchmark.avg_vacancy_rate > 0 && (
                <div>
                  <p className="text-[10px] text-zinc-500">Avg Vacancy</p>
                  <p className="font-mono text-sm text-zinc-500">{industryBenchmark.avg_vacancy_rate}%</p>
                </div>
              )}
              {industryBenchmark.avg_rent_growth != null && industryBenchmark.avg_rent_growth !== 0 && (
                <div>
                  <p className="text-[10px] text-zinc-500">Avg Rent Growth</p>
                  <p className="font-mono text-sm text-zinc-500">{industryBenchmark.avg_rent_growth}%</p>
                </div>
              )}
              {!industryBenchmark.prospect_market_vacancy && !industryBenchmark.prospect_market_rent_growth && (
                <div className="col-span-2 text-xs text-zinc-500">No benchmark data available</div>
              )}
            </div>
          </div>
        )}

        {/* Decision Maker Context */}
        {(decisionMaker.company_size_tier || decisionMaker.typical_buyer || decisionMaker.primary_pain_point || decisionMaker.what_they_google) && (
          <div className="rounded-lg border border-zinc-800">
            <div className="flex items-center gap-2 border-b border-zinc-800 bg-zinc-900/50 px-3 py-1.5">
              <Building2 className="h-3.5 w-3.5 text-zinc-500" />
              <h3 className="text-xs font-medium text-zinc-300">Decision Maker Profile</h3>
            </div>
            <div className="p-2 space-y-1">
              {decisionMaker.company_size_tier && (
                <div className="flex items-center justify-between text-xs py-1">
                  <span className="text-zinc-500 shrink-0">Company Size</span>
                  <span className="text-zinc-300 text-right max-w-[200px] truncate ml-4">{decisionMaker.company_size_tier}</span>
                </div>
              )}
              {decisionMaker.typical_buyer && (
                <div className="flex items-center justify-between text-xs py-1">
                  <span className="text-zinc-500 shrink-0">Typical Buyer</span>
                  <span className="text-zinc-300 text-right max-w-[200px] truncate ml-4">{decisionMaker.typical_buyer}</span>
                </div>
              )}
              {decisionMaker.primary_pain_point && (
                <div className="flex items-start justify-between text-xs py-1">
                  <span className="text-zinc-500 shrink-0">Primary Pain</span>
                  <span className="text-zinc-300 text-right max-w-[200px] ml-4">{decisionMaker.primary_pain_point}</span>
                </div>
              )}
              {decisionMaker.what_they_google && (
                <div className="flex items-center justify-between text-xs py-1">
                  <span className="text-zinc-500 shrink-0">Google Search</span>
                  <span className="text-zinc-400 text-right max-w-[200px] truncate ml-4">{decisionMaker.what_they_google}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Talking Points */}
        {talkingPoints.length > 0 && (
          <div className="rounded-lg border border-zinc-800">
            <div className="flex items-center gap-2 border-b border-zinc-800 bg-zinc-900/50 px-3 py-1.5">
              <TrendingUp className="h-3.5 w-3.5 text-zinc-500" />
              <h3 className="text-xs font-medium text-zinc-300">Talking Points</h3>
            </div>
            <div className="space-y-1 p-2">
              {talkingPoints.map((point, i) => (
                <div key={i} className="flex items-start gap-2 text-xs">
                  <span className="mt-1 h-1.5 w-1.5 rounded-full bg-indigo-500"></span>
                  <span className="text-zinc-400">{point}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Buying Signals */}
        {(buying.expansion_detected || buying.funding_detected || buying.leadership_change || buying.portfolio_growth) && (
          <div className="rounded-lg border border-zinc-800 bg-zinc-900/50">
            <div className="flex items-center gap-2 border-b border-zinc-800 bg-zinc-900/50 px-3 py-1.5">
              <TrendingUp className="h-3.5 w-3.5 text-zinc-500" />
              <h3 className="text-xs font-medium text-zinc-300">Buying Signals</h3>
            </div>
            <div className="space-y-1 p-2">
              {buying.expansion_detected && <SignalItem label="Expansion" detail={buying.expansion_detail} />}
              {buying.funding_detected && <SignalItem label="Funding" detail={buying.funding_detail} />}
              {buying.leadership_change && <SignalItem label="Leadership" detail={buying.leadership_detail} />}
              {buying.portfolio_growth && <SignalItem label="Portfolio" detail={buying.portfolio_detail} />}
            </div>
          </div>
        )}

        {/* Email Draft */}
        {emailSubject || emailBody ? (
          <div className="rounded-lg border border-zinc-800">
            <div className="flex items-center justify-between border-b border-zinc-800 bg-zinc-900/50 px-3 py-1.5">
              <div className="flex items-center gap-2">
                <Copy className="h-3.5 w-3.5 text-zinc-500" />
                <h3 className="text-xs font-medium text-zinc-300">Email Draft</h3>
              </div>
              <button
                onClick={onCopyEmail}
                className="flex items-center gap-1 rounded bg-indigo-600 px-2 py-1 text-xs text-white hover:bg-indigo-700"
              >
                <Copy className="h-3 w-3" />
                Copy
              </button>
            </div>
            <div className="space-y-2 p-2">
              {emailSubject && (
                <div>
                  <p className="text-[10px] font-medium text-zinc-500">Subject</p>
                  <p className="text-xs font-medium text-zinc-300">{emailSubject}</p>
                </div>
              )}
              <div className="whitespace-pre-wrap rounded bg-zinc-900/50 p-2 text-xs text-zinc-400">
                {emailBody}
              </div>
            </div>
          </div>
        ) : null}

        {/* Objection Handling */}
        {objectionHandling && Object.keys(objectionHandling).length > 0 && (
          <div className="rounded-lg border border-zinc-800">
            <div className="flex items-center gap-2 border-b border-zinc-800 bg-zinc-900/50 px-3 py-1.5">
              <Shield className="h-3.5 w-3.5 text-zinc-500" />
              <h3 className="text-xs font-medium text-zinc-300">Objection Handling</h3>
            </div>
            <div className="grid grid-cols-2 gap-2 p-2">
              {Object.entries(objectionHandling).map(([key, value]) => {
                if (!value || (typeof value === 'string' && value.trim().length === 0)) return null;
                const labelMap: Record<string, string> = {
                  has_yardi: "Has Yardi",
                  too_expensive: "Too Expensive",
                  have_team: "Have Team",
                  not_priority: "Not Priority",
                  current_solution: "Current Solution",
                };
                const label = labelMap[key] || key.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim();
                return (
                  <div key={key} className="rounded bg-zinc-900/50 p-2">
                    <p className="mb-1 text-[10px] font-medium text-zinc-400 uppercase">{label}</p>
                    <p className="text-xs text-zinc-300 leading-tight">{value}</p>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Market Context */}
        {(roiEstimate.market_renter_pct != null || roiEstimate.market_vacancy != null || kdp.renter_pct != null || kdp.vacancy_rate != null) && (
          <div className="rounded-lg border border-zinc-800">
            <div className="flex items-center gap-2 border-b border-zinc-800 bg-zinc-900/50 px-3 py-1.5">
              <DollarSign className="h-3.5 w-3.5 text-zinc-500" />
              <h3 className="text-xs font-medium text-zinc-300">Market Context</h3>
            </div>
            <div className="grid grid-cols-2 gap-2 p-2">
              {(roiEstimate.market_renter_pct ?? kdp.renter_pct ?? null) !== null && (
                <div>
                  <p className="text-[10px] text-zinc-500">Renter Market</p>
                  <p className="font-mono text-sm text-zinc-300">{roiEstimate.market_renter_pct ?? kdp.renter_pct}%</p>
                </div>
              )}
              {(roiEstimate.market_vacancy ?? kdp.vacancy_rate ?? null) !== null && (
                <div>
                  <p className="text-[10px] text-zinc-500">Vacancy</p>
                  <p className={`font-mono text-sm ${(roiEstimate.market_vacancy ?? kdp.vacancy_rate ?? 0) < 5 ? 'text-emerald-400' : 'text-zinc-300'}`}>
                    {roiEstimate.market_vacancy ?? kdp.vacancy_rate}%
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 border-t border-zinc-800 p-4">
        <button
          onClick={onResendToSlack}
          className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
        >
          <Send className="h-4 w-4" />
          Post to Slack
        </button>
        <button
          onClick={onExportToSheets}
          className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-zinc-700 px-4 py-2 text-sm font-medium text-zinc-300 hover:bg-zinc-800"
        >
          <ExternalLink className="h-4 w-4" />
          Export to Sheets
        </button>
      </div>
    </div>
  );
}

function SignalItem({ label, detail }: { label: string; detail?: string | null }) {
  return (
    <div className="flex items-start gap-2 text-xs">
      <span className="mt-1 h-1.5 w-1.5 rounded-full bg-zinc-600"></span>
      <div>
        <span className="font-medium text-zinc-300">{label}</span>
        {detail && <span className="text-zinc-500"> - {detail}</span>}
      </div>
    </div>
  );
}
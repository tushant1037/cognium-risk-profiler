import type {
  AssessmentPreview,
  AssessmentRecord,
} from "../types";
import { Icon } from "./Icon";

function titleCase(value: string) {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function money(value: number, currency: string) {
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(value);
}

function percentage(value: number | null | undefined, digits = 1) {
  return value === null || value === undefined ? "—" : `${value.toFixed(digits)}%`;
}

function ScoreMeter({
  title,
  value,
  profile,
  tone,
}: {
  title: string;
  value: number;
  profile: string;
  tone: "green" | "blue";
}) {
  return (
    <div className={`score-card ${tone}`}>
      <div className="score-card-top">
        <div>
          <span className="metric-label">{title}</span>
          <div className="score-value">{Math.round(value)}<small>/100</small></div>
        </div>
        <span className="score-icon"><Icon name={tone === "green" ? "wallet" : "activity"} /></span>
      </div>
      <div className="score-track"><span style={{ width: `${Math.min(100, Math.max(0, value))}%` }} /></div>
      <div className="score-foot"><span>Risk band</span><strong>{titleCase(profile)}</strong></div>
    </div>
  );
}

function AllocationBars({
  allocations,
  currency,
}: {
  allocations: AssessmentPreview["recommendation"]["sleeve_allocations"];
  currency: string;
}) {
  const colors = ["#287e66", "#84ac96", "#c7d9cf", "#bb9c68", "#8da9c5"];
  return (
    <div className="allocation-list">
      {allocations.map((item, index) => (
        <div className="allocation-row" key={`${item.sleeve}-${index}`}>
          <div className="allocation-heading">
            <span className="allocation-name">
              <i style={{ backgroundColor: colors[index % colors.length] }} />
              {item.display_name}
            </span>
            <strong>{percentage(item.target_pct)}</strong>
          </div>
          <div className="allocation-track">
            <span
              style={{
                width: `${Math.min(100, Math.max(0, item.target_pct))}%`,
                backgroundColor: colors[index % colors.length],
              }}
            />
          </div>
          <div className="allocation-detail">
            <span>{item.asset_class}</span>
            <span>{money(item.notional_initial, currency)} initial</span>
          </div>
        </div>
      ))}
    </div>
  );
}

export function RecommendationView({
  result,
  savedRecord,
  isSaving,
  onSave,
  onEdit,
  onNew,
  readOnly = false,
}: {
  result: AssessmentPreview;
  savedRecord: AssessmentRecord | null;
  isSaving: boolean;
  onSave: () => void;
  onEdit: () => void;
  onNew: () => void;
  readOnly?: boolean;
}) {
  const { assessment, recommendation } = result;
  const metrics = recommendation.portfolio_metrics;
  const profile = titleCase(assessment.final_profile);

  return (
    <section className="content-column results-column">
      <div className="result-banner">
        <div className="result-banner-main">
          <span className="result-kicker"><Icon name="check" size={14} /> {readOnly ? "SAVED ASSESSMENT" : "YOUR ASSESSMENT IS READY"}</span>
          <h1>{readOnly ? <>Your profile, <em>at that time.</em></> : <>A profile built around <em>you.</em></>}</h1>
          <p>
            {readOnly
              ? "This is the recommendation saved with this historical assessment."
              : "We combined your financial capacity and comfort with risk to create a clear starting point for your portfolio."}
          </p>
        </div>
        <div className="profile-seal">
          <span>YOUR PROFILE</span>
          <strong>{profile}</strong>
          <small>{assessment.final_profile === assessment.unconstrained_profile ? "Profile confirmed" : "Adjusted for your circumstances"}</small>
        </div>
        <div className="banner-decoration" aria-hidden="true"><span /><span /><span /></div>
      </div>

      <div className="scores-grid">
        <ScoreMeter
          title="Risk capacity"
          value={assessment.capacity_score}
          profile={assessment.capacity_tier}
          tone="green"
        />
        <ScoreMeter
          title="Risk tolerance"
          value={assessment.tolerance_score}
          profile={assessment.tolerance_tier}
          tone="blue"
        />
      </div>

      {assessment.knockout_rules_applied.length > 0 && (
        <div className="notice-card">
          <span className="notice-icon"><Icon name="shield" /></span>
          <div>
            <strong>Your circumstances shaped the result</strong>
            <p>{assessment.knockout_rules_applied.map((rule) => rule.reason).join(" ")}</p>
          </div>
        </div>
      )}

      <div className="section-heading-row">
        <div>
          <p className="eyebrow">THE RECOMMENDATION</p>
          <h2>A portfolio with a clear purpose.</h2>
        </div>
        <span className="source-chip">
          <span className="source-dot" />
          {recommendation.market_data_source.replaceAll("_", " ")}
        </span>
      </div>

      <div className="metrics-grid">
        <div className="metric-card featured">
          <span className="metric-label">Starting amount</span>
          <strong>{money(recommendation.initial_investment, recommendation.base_currency)}</strong>
          <span className="metric-sub">Planned for your portfolio</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Monthly contribution</span>
          <strong>{money(recommendation.planned_monthly_contribution, recommendation.base_currency)}</strong>
          <span className="metric-sub">Added each month</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Weighted fund cost</span>
          <strong>{percentage(metrics.weighted_expense_ratio_pct, 2)}</strong>
          <span className="metric-sub">Annual expense ratio</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Distribution yield</span>
          <strong>{percentage(metrics.weighted_distribution_yield_pct, 2)}</strong>
          <span className="metric-sub">Historical portfolio yield</span>
        </div>
      </div>

      <div className="two-column-layout">
        <article className="panel allocation-panel">
          <div className="panel-heading">
            <div>
              <span className="panel-overline">TARGET MIX</span>
              <h3>Where your money goes</h3>
            </div>
            <span className="panel-icon"><Icon name="activity" /></span>
          </div>
          <AllocationBars
            allocations={recommendation.sleeve_allocations}
            currency={recommendation.base_currency}
          />
          <div className="allocation-legend">
            <span>Equities <b>{percentage(metrics.equity_pct)}</b></span>
            <span>Fixed income <b>{percentage(metrics.fixed_income_pct)}</b></span>
            <span>Cash & alternatives <b>{percentage(metrics.cash_pct + metrics.alternatives_pct)}</b></span>
          </div>
        </article>
        <article className="panel explanation-panel">
          <div className="panel-heading">
            <div>
              <span className="panel-overline">A NOTE FOR YOU</span>
              <h3>Why this profile?</h3>
            </div>
            <span className="panel-icon"><Icon name="sparkles" /></span>
          </div>
          <p className="explanation-copy">{assessment.explanation}</p>
          <div className="narrative-copy">{recommendation.narrative_summary}</div>
          {recommendation.constraint_notes.length > 0 && (
            <div className="constraint-notes">
              {recommendation.constraint_notes.map((note) => (
                <p key={note}><Icon name="shield" size={15} /> {note}</p>
              ))}
            </div>
          )}
        </article>
      </div>

      <div className="panel holdings-panel">
        <div className="panel-heading">
          <div>
            <span className="panel-overline">SELECTED INSTRUMENTS</span>
            <h3>What’s in your portfolio</h3>
          </div>
          <span className="holdings-count">{recommendation.holdings.length} funds</span>
        </div>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Fund</th>
                <th>Allocation</th>
                <th>Amount</th>
                <th>1Y return</th>
                <th>Risk · volatility</th>
                <th>Expense</th>
              </tr>
            </thead>
            <tbody>
              {recommendation.holdings.map((holding) => (
                <tr key={holding.ticker}>
                  <td>
                    <div className="fund-name"><strong>{holding.ticker}</strong><span>{holding.name}</span></div>
                  </td>
                  <td><strong>{percentage(holding.weight_pct)}</strong></td>
                  <td>{money(holding.notional_initial, recommendation.base_currency)}</td>
                  <td>{percentage(holding.return_1y_pct)}</td>
                  <td>{percentage(holding.volatility_1y_pct)}</td>
                  <td>{percentage(holding.expense_ratio_pct, 2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="table-footnote">
          Historical returns and volatility are backward-looking and do not predict future results.
        </p>
      </div>

      {savedRecord && (
        <div className="integrity-card">
          <span className="integrity-mark"><Icon name="shield" /></span>
          <div>
            <strong>Assessment saved and integrity-protected</strong>
            <p>Record {savedRecord.id} · {new Date(savedRecord.created_at).toLocaleString()}</p>
          </div>
          <span className="verified-pill"><Icon name="check" size={14} /> Saved</span>
        </div>
      )}

      {!readOnly && (
        <div className="result-actions">
          <div className="result-action-left">
            <button className="button button-quiet" type="button" onClick={onEdit}>
              <Icon name="arrow-left" size={16} /> Review answers
            </button>
            {savedRecord && (
              <button className="button button-quiet" type="button" onClick={onNew}>
                <Icon name="plus" size={16} /> New assessment
              </button>
            )}
          </div>
          <button
            className="button button-primary"
            type="button"
            onClick={onSave}
            disabled={isSaving || Boolean(savedRecord)}
          >
            {isSaving ? <><span className="spinner" /> Saving record</> : savedRecord ? <><Icon name="check" size={16} /> Assessment saved</> : <>Save assessment <Icon name="arrow-right" size={16} /></>}
          </button>
        </div>
      )}
      <p className="disclaimer-copy">
        This is an educational exercise, not financial advice. Returns, yields and drawdowns shown
        are historical and are not forecasts. Consider speaking with a qualified financial adviser.
      </p>
    </section>
  );
}

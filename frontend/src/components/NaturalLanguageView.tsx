import { useState } from "react";
import type { ReactNode } from "react";
import { getNaturalLanguageRecommendation } from "../api";
import type { NaturalLanguageResponse } from "../types";
import { Icon } from "./Icon";

const prompts = [
  "Low-fee US stock funds, no crypto",
  "Income-focused government and corporate bonds",
  "Technology growth funds with reasonable fees",
  "Strictly Sharia-compliant funds",
];

function Tag({ children }: { children: ReactNode }) {
  return <span className="result-tag">{children}</span>;
}

export function NaturalLanguageView() {
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState<NaturalLanguageResponse | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setResult(null);
    setIsLoading(true);
    try {
      setResult(await getNaturalLanguageRecommendation(prompt.trim()));
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "We couldn’t process that request. Please try again.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="content-column natural-column">
      <div className="page-heading">
        <div>
          <p className="eyebrow">A MORE NATURAL WAY TO EXPLORE</p>
          <h1>Tell us what you’re looking for.</h1>
          <p className="page-subtitle">
            Describe your investing preferences in your own words. We’ll find
            funds in the verified universe that match.
          </p>
        </div>
        <span className="ai-mark"><Icon name="sparkles" size={20} /></span>
      </div>

      <div className="natural-hero">
        <div className="natural-orbit orbit-one" />
        <div className="natural-orbit orbit-two" />
        <span className="natural-label"><Icon name="sparkles" size={15} /> PLAIN LANGUAGE · DATA-GROUNDED</span>
        <h2>Your goals, in your words.</h2>
        <p>
          Try a theme, a fee limit, an income preference, or a set of screening rules.
        </p>
        <form className="prompt-form" onSubmit={submit}>
          <label htmlFor="natural-prompt" className="sr-only">Describe your investment preferences</label>
          <textarea
            id="natural-prompt"
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            placeholder="I’m looking for low-cost funds for long-term growth, with no crypto exposure..."
            maxLength={2000}
            rows={4}
            required
            minLength={3}
          />
          <div className="prompt-bottom">
            <span>{prompt.length}/2000 · Filters are applied to our ETF universe</span>
            <button className="button button-primary" type="submit" disabled={isLoading || prompt.trim().length < 3}>
              {isLoading ? <><span className="spinner" /> Finding matches</> : <>Find matching funds <Icon name="arrow-right" size={16} /></>}
            </button>
          </div>
        </form>
        <div className="prompt-suggestions">
          <span>TRY AN EXAMPLE</span>
          {prompts.map((example) => (
            <button type="button" key={example} onClick={() => setPrompt(example)}>
              {example} <Icon name="arrow-right" size={13} />
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="error-card" role="alert">
          <span className="error-icon"><Icon name="close" /></span>
          <div><strong>We couldn’t complete that search</strong><p>{error}</p></div>
        </div>
      )}

      {result && (
        <div className="natural-results">
          <div className="section-heading-row results-heading">
            <div>
              <p className="eyebrow">YOUR MATCHES</p>
              <h2>{result.count} {result.count === 1 ? "fund" : "funds"} match your filters</h2>
            </div>
            <span className="source-chip"><span className="source-dot" /> Verified ETF universe</span>
          </div>

          <div className="intent-summary panel">
            <div className="intent-summary-title"><Icon name="filter" size={16} /> FILTERS APPLIED</div>
            <div className="intent-tags">
              {result.filters.preferred_sleeves.map((value) => <Tag key={`s-${value}`}>{value.replaceAll("_", " ")}</Tag>)}
              {result.filters.preferred_categories.map((value) => <Tag key={`c-${value}`}>{value}</Tag>)}
              {result.filters.preferred_regions.map((value) => <Tag key={`r-${value}`}>{value.replaceAll("_", " ")}</Tag>)}
              {result.filters.max_expense_ratio_pct !== null && <Tag>Fee ≤ {result.filters.max_expense_ratio_pct}%</Tag>}
              {result.filters.min_distribution_yield_pct !== null && <Tag>Yield ≥ {result.filters.min_distribution_yield_pct}%</Tag>}
              {result.filters.exclude_crypto && <Tag>No crypto</Tag>}
              {result.filters.require_esg && <Tag>ESG screened</Tag>}
              {result.filters.require_sharia_compliant && <Tag>Sharia compliant</Tag>}
              {!result.filters.preferred_sleeves.length &&
                !result.filters.preferred_categories.length &&
                !result.filters.preferred_regions.length &&
                result.filters.max_expense_ratio_pct === null &&
                result.filters.min_distribution_yield_pct === null &&
                !result.filters.exclude_crypto &&
                !result.filters.require_esg &&
                !result.filters.require_sharia_compliant && <Tag>Broad universe · no hard filters</Tag>}
            </div>
            <p className="ai-narrative"><Icon name="sparkles" size={16} /> {result.narrative}</p>
          </div>

          {result.count === 0 ? (
            <div className="empty-state panel">
              <span className="empty-icon"><Icon name="search" size={25} /></span>
              <h3>No funds matched this combination</h3>
              <p>Try broadening your request or relaxing one of the filters.</p>
            </div>
          ) : (
            <div className="natural-fund-grid">
              {result.matched_instruments.map((instrument) => (
                <article className="fund-card panel" key={instrument.ticker}>
                  <div className="fund-card-top">
                    <span className="fund-ticker">{instrument.ticker}</span>
                    {instrument.sharia_compliant && <Tag>Sharia</Tag>}
                    {!instrument.sharia_compliant && instrument.esg && <Tag>ESG</Tag>}
                  </div>
                  <h3>{instrument.name}</h3>
                  <div className="fund-card-tags">
                    <Tag>{instrument.sleeve.replaceAll("_", " ")}</Tag>
                    <Tag>{instrument.region.replaceAll("_", " ")}</Tag>
                    {instrument.category && <Tag>{instrument.category}</Tag>}
                  </div>
                  <div className="fund-stat-row">
                    <div><span>Expense ratio</span><strong>{instrument.expense_ratio_pct === null ? "—" : `${instrument.expense_ratio_pct}%`}</strong></div>
                    <div><span>Distribution yield</span><strong>{instrument.distribution_yield_pct === null ? "—" : `${instrument.distribution_yield_pct}%`}</strong></div>
                  </div>
                  <p className="justification">{instrument.justification}</p>
                </article>
              ))}
            </div>
          )}
          <p className="disclaimer-copy">
            Matches are selected by deterministic filters over the ETF universe. This is not investment advice.
          </p>
        </div>
      )}
    </section>
  );
}

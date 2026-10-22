import { useEffect, useState } from "react";
import { options, preferenceCards } from "../formOptions";
import type {
  BaseCurrency,
  DrawdownReaction,
  EmergencyFund,
  Exclusion,
  IncomeStability,
  InvestmentExperience,
  InvestmentHorizon,
  MaxAcceptableLoss,
  PortfolioPreference,
  PrimaryGoal,
  QuestionnaireSubmission,
  ShareOfLiquidNetWorth,
} from "../types";
import { Icon } from "./Icon";

type Draft = {
  capacity: {
    birthYear: string;
    investmentHorizon: InvestmentHorizon | "";
    initialInvestment: string;
    monthlyContribution: string;
    emergencyFund: EmergencyFund | "";
    incomeStability: IncomeStability | "";
    shareOfLiquidNetWorth: ShareOfLiquidNetWorth | "";
    withdrawalExpectation: boolean | null;
  };
  tolerance: {
    primaryGoal: PrimaryGoal | "";
    drawdownReaction: DrawdownReaction | "";
    maxLoss: MaxAcceptableLoss | "";
    preference: PortfolioPreference | "";
    experience: InvestmentExperience | "";
  };
  baseCurrency: BaseCurrency;
  exclusions: Exclusion[];
  circumstances: string;
};

const initialDraft: Draft = {
  capacity: {
    birthYear: "",
    investmentHorizon: "",
    initialInvestment: "",
    monthlyContribution: "0",
    emergencyFund: "",
    incomeStability: "",
    shareOfLiquidNetWorth: "",
    withdrawalExpectation: null,
  },
  tolerance: {
    primaryGoal: "",
    drawdownReaction: "",
    maxLoss: "",
    preference: "",
    experience: "",
  },
  baseCurrency: "USD",
  exclusions: ["none"],
  circumstances: "",
};

const withdrawalOptions: readonly [boolean, string][] = [
  [false, "No, unlikely"],
  [true, "Yes, I may"],
];

function required<T extends string>(value: T | "", label: string): T {
  if (!value) throw new Error(`Please answer: ${label}.`);
  return value;
}

function SelectField<T extends string>({
  label,
  value,
  choices,
  onChange,
}: {
  label: string;
  value: T | "";
  choices: readonly (readonly [T, string])[];
  onChange: (value: T | "") => void;
}) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      <span className="select-wrap">
        <select
          value={value}
          onChange={(event) => {
            const selected =
              choices.find(([choice]) => choice === event.target.value)?.[0] ?? "";
            onChange(selected);
          }}
        >
          <option value="">Choose an answer</option>
          {choices.map(([choice, text]) => (
            <option value={choice} key={choice}>
              {text}
            </option>
          ))}
        </select>
        <Icon name="chevron-down" size={16} />
      </span>
    </label>
  );
}

function TextField({
  label,
  value,
  onChange,
  type = "text",
  placeholder,
  min,
  max,
  prefix,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  placeholder?: string;
  min?: number;
  max?: number;
  prefix?: string;
}) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      <span className={`input-wrap ${prefix ? "has-prefix" : ""}`}>
        {prefix && <span className="input-prefix">{prefix}</span>}
        <input
          type={type}
          value={value}
          placeholder={placeholder ?? (type === "number" ? "0" : "Your answer")}
          min={min}
          max={max}
          onChange={(event) => onChange(event.target.value)}
        />
      </span>
    </label>
  );
}

function ChoiceCards<T extends string>({
  label,
  value,
  choices,
  onChange,
}: {
  label: string;
  value: T | "";
  choices: readonly (readonly [T, string])[];
  onChange: (value: T) => void;
}) {
  return (
    <fieldset className="choice-fieldset">
      <legend className="field-label">{label}</legend>
      <div className="choice-grid">
        {choices.map(([choice, text]) => (
          <button
            className={`choice-button ${value === choice ? "selected" : ""}`}
            type="button"
            key={choice}
            aria-pressed={value === choice}
            onClick={() => onChange(choice)}
          >
            <span className="choice-dot" />
            {text}
          </button>
        ))}
      </div>
    </fieldset>
  );
}

export function Questionnaire({
  isBusy,
  onPreview,
}: {
  isBusy: boolean;
  onPreview: (submission: QuestionnaireSubmission) => void;
}) {
  const [draft, setDraft] = useState<Draft>(initialDraft);
  const [step, setStep] = useState(0);
  const [formError, setFormError] = useState("");

  useEffect(() => {
    if (step > 0) window.scrollTo({ top: 0, behavior: "smooth" });
  }, [step]);

  const updateCapacity = <K extends keyof Draft["capacity"]>(
    key: K,
    value: Draft["capacity"][K],
  ) => {
    setDraft((current) => ({
      ...current,
      capacity: { ...current.capacity, [key]: value },
    }));
  };

  const updateTolerance = <K extends keyof Draft["tolerance"]>(
    key: K,
    value: Draft["tolerance"][K],
  ) => {
    setDraft((current) => ({
      ...current,
      tolerance: { ...current.tolerance, [key]: value },
    }));
  };

  const continueToNext = () => {
    setFormError("");
    try {
      if (step === 0) {
        const birthYear = Number(draft.capacity.birthYear);
        const initialInvestment = Number(draft.capacity.initialInvestment);
        const earliestBirthYear = Math.max(1900, new Date().getFullYear() - 105);
        if (!draft.capacity.birthYear || !Number.isInteger(birthYear)) {
          throw new Error("Enter a valid year of birth.");
        }
        if (
          birthYear < earliestBirthYear ||
          birthYear > new Date().getFullYear() - 18
        ) {
          throw new Error("Enter a year corresponding to an age between 18 and 105.");
        }
        if (!Number.isFinite(initialInvestment) || initialInvestment < 100) {
          throw new Error("Initial investment must be at least 100.");
        }
        const monthlyContribution = Number(draft.capacity.monthlyContribution);
        if (
          draft.capacity.monthlyContribution === "" ||
          !Number.isFinite(monthlyContribution) ||
          monthlyContribution < 0
        ) {
          throw new Error("Monthly contribution must be zero or more.");
        }
        required(draft.capacity.investmentHorizon, "investment horizon");
        required(draft.capacity.emergencyFund, "emergency fund");
        required(draft.capacity.incomeStability, "income stability");
        required(draft.capacity.shareOfLiquidNetWorth, "share of liquid net worth");
      }
      if (step === 1) {
        required(draft.tolerance.primaryGoal, "primary goal");
        required(draft.tolerance.drawdownReaction, "reaction to a market drop");
        required(draft.tolerance.maxLoss, "maximum acceptable loss");
        required(draft.tolerance.preference, "portfolio preference");
        required(draft.tolerance.experience, "investment experience");
      }
      if (step < 2) {
        setStep((current) => current + 1);
        return;
      }
      if (draft.capacity.withdrawalExpectation === null) {
        throw new Error("Please answer whether you expect to make a large withdrawal.");
      }
      const submission: QuestionnaireSubmission = {
        capacity: {
          birth_year: Number(draft.capacity.birthYear),
          investment_horizon: required(
            draft.capacity.investmentHorizon,
            "investment horizon",
          ),
          initial_investment_amount: Number(draft.capacity.initialInvestment),
          planned_monthly_contribution: Number(draft.capacity.monthlyContribution),
          emergency_fund: required(draft.capacity.emergencyFund, "emergency fund"),
          income_stability: required(draft.capacity.incomeStability, "income stability"),
          share_of_liquid_net_worth: required(
            draft.capacity.shareOfLiquidNetWorth,
            "share of liquid net worth",
          ),
          withdrawal_expectation: draft.capacity.withdrawalExpectation,
        },
        tolerance: {
          primary_goal: required(draft.tolerance.primaryGoal, "primary goal"),
          reaction_to_drawdown: required(
            draft.tolerance.drawdownReaction,
            "reaction to a market drop",
          ),
          max_acceptable_loss: required(draft.tolerance.maxLoss, "maximum acceptable loss"),
          portfolio_preference: required(draft.tolerance.preference, "portfolio preference"),
          investment_experience: required(
            draft.tolerance.experience,
            "investment experience",
          ),
        },
        constraints: {
          base_currency: draft.baseCurrency,
          exclusions: draft.exclusions,
        },
        additional_circumstances: draft.circumstances.trim() || null,
      };
      onPreview(submission);
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "Check your answers.");
    }
  };

  const toggleExclusion = (exclusion: Exclusion) => {
    setDraft((current) => {
      if (exclusion === "none") return { ...current, exclusions: ["none"] };
      const selected = current.exclusions.filter((item) => item !== "none");
      const next = selected.includes(exclusion)
        ? selected.filter((item) => item !== exclusion)
        : [...selected, exclusion];
      return { ...current, exclusions: next.length ? next : ["none"] };
    });
  };

  const stepNames = ["Risk capacity", "Risk tolerance", "Your preferences"];
  const inputPrefix =
    draft.baseCurrency === "USD" || draft.baseCurrency === "AED"
      ? draft.baseCurrency
      : draft.baseCurrency;

  return (
    <section className="content-column">
      <div className="page-heading">
        <div>
          <p className="eyebrow">YOUR PERSONAL RISK PROFILE</p>
          <h1>Let’s understand what matters to you.</h1>
          <p className="page-subtitle">
            A few thoughtful questions help shape a recommendation around your
            circumstances, not just the numbers.
          </p>
        </div>
        <span className="time-chip"><Icon name="clock" size={15} /> About 4 minutes</span>
      </div>

      <div className="wizard-card">
        <div className="wizard-topline">
          <div className="step-count">STEP 0{step + 1} <span>OF 03</span></div>
          <div className="wizard-progress" aria-label={`Step ${step + 1} of 3`}>
            {stepNames.map((name, index) => (
              <span
                className={`progress-segment ${index <= step ? "active" : ""}`}
                key={name}
              />
            ))}
          </div>
        </div>
        <div className="wizard-title-row">
          <div>
            <h2>{stepNames[step]}</h2>
            <p className="muted">
              {step === 0 && "Your financial capacity and time horizon."}
              {step === 1 && "How you feel about uncertainty and market movement."}
              {step === 2 && "The preferences and principles you want us to respect."}
            </p>
          </div>
          <span className="step-icon">
            <Icon name={step === 0 ? "wallet" : step === 1 ? "activity" : "shield"} />
          </span>
        </div>

        {step === 0 && (
          <div className="form-grid">
            <TextField
              label="Year of birth"
              type="number"
              min={Math.max(1900, new Date().getFullYear() - 105)}
              max={new Date().getFullYear() - 18}
              placeholder="e.g. 1985"
              value={draft.capacity.birthYear}
              onChange={(value) => updateCapacity("birthYear", value)}
            />
            <SelectField
              label="How long do you expect to invest?"
              value={draft.capacity.investmentHorizon}
              choices={options.investmentHorizon}
              onChange={(value) => updateCapacity("investmentHorizon", value)}
            />
            <TextField
              label="Initial investment"
              type="number"
              min={100}
              placeholder="e.g. 25000"
              prefix={inputPrefix}
              value={draft.capacity.initialInvestment}
              onChange={(value) => updateCapacity("initialInvestment", value)}
            />
            <TextField
              label="Monthly contribution"
              type="number"
              min={0}
              placeholder="0"
              prefix={inputPrefix}
              value={draft.capacity.monthlyContribution}
              onChange={(value) => updateCapacity("monthlyContribution", value)}
            />
            <SelectField
              label="Emergency savings"
              value={draft.capacity.emergencyFund}
              choices={options.emergencyFund}
              onChange={(value) => updateCapacity("emergencyFund", value)}
            />
            <SelectField
              label="How predictable is your income?"
              value={draft.capacity.incomeStability}
              choices={options.incomeStability}
              onChange={(value) => updateCapacity("incomeStability", value)}
            />
            <SelectField
              label="Share of liquid net worth invested"
              value={draft.capacity.shareOfLiquidNetWorth}
              choices={options.shareOfLiquidNetWorth}
              onChange={(value) => updateCapacity("shareOfLiquidNetWorth", value)}
            />
            <div className="field full-width">
              <span className="field-label">
                Might you need to withdraw more than 25% within 3 years?
              </span>
              <div className="choice-grid two-choice">
                {withdrawalOptions.map(([value, label]) => (
                  <button
                    className={`choice-button ${
                      draft.capacity.withdrawalExpectation === value ? "selected" : ""
                    }`}
                    type="button"
                    key={String(value)}
                    aria-pressed={draft.capacity.withdrawalExpectation === value}
                    onClick={() => updateCapacity("withdrawalExpectation", value)}
                  >
                    <span className="choice-dot" />
                    {label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {step === 1 && (
          <div className="form-stack">
            <SelectField
              label="What is your primary goal?"
              value={draft.tolerance.primaryGoal}
              choices={options.primaryGoal}
              onChange={(value) => updateTolerance("primaryGoal", value)}
            />
            <ChoiceCards
              label="If your investments fell 20% in three months, what would you do?"
              value={draft.tolerance.drawdownReaction}
              choices={options.drawdownReaction}
              onChange={(value) => updateTolerance("drawdownReaction", value)}
            />
            <ChoiceCards
              label="What is the largest one-year loss you could accept?"
              value={draft.tolerance.maxLoss}
              choices={options.maxLoss}
              onChange={(value) => updateTolerance("maxLoss", value)}
            />
            <fieldset className="choice-fieldset">
              <legend className="field-label">Which historical mix feels right?</legend>
              <p className="helper-copy">
                Rounded historical figures, not a forecast or promise of future returns.
              </p>
              <div className="preference-grid">
                {preferenceCards.map((card) => (
                  <button
                    type="button"
                    className={`preference-card ${
                      draft.tolerance.preference === card.value ? "selected" : ""
                    }`}
                    key={card.value}
                    aria-pressed={draft.tolerance.preference === card.value}
                    onClick={() => updateTolerance("preference", card.value)}
                  >
                    <span className="preference-letter">OPTION {card.value}</span>
                    <strong>{card.label}</strong>
                    <span>{card.returnText}</span>
                    <span>{card.fallText}</span>
                    <small>{card.mix}</small>
                  </button>
                ))}
              </div>
            </fieldset>
            <SelectField
              label="What investment experience do you have?"
              value={draft.tolerance.experience}
              choices={options.experience}
              onChange={(value) => updateTolerance("experience", value)}
            />
          </div>
        )}

        {step === 2 && (
          <div className="form-stack">
            <SelectField
              label="Base currency"
              value={draft.baseCurrency}
              choices={options.currency}
              onChange={(value) => {
                if (value) setDraft((current) => ({ ...current, baseCurrency: value }));
              }}
            />
            <fieldset className="choice-fieldset">
              <legend className="field-label">Any investment preferences?</legend>
              <p className="helper-copy">
                Select all that apply. These are applied as firm filters.
              </p>
              <div className="preference-chip-grid">
                <button
                  type="button"
                  className={`filter-chip ${draft.exclusions.includes("none") ? "selected" : ""}`}
                  aria-pressed={draft.exclusions.includes("none")}
                  onClick={() => toggleExclusion("none")}
                >
                  <span className="chip-check"><Icon name="check" size={13} /></span>
                  No preferences
                </button>
                {options.exclusions.map(([exclusion, label]) => (
                  <button
                    type="button"
                    className={`filter-chip ${
                      draft.exclusions.includes(exclusion) ? "selected" : ""
                    }`}
                    aria-pressed={draft.exclusions.includes(exclusion)}
                    key={exclusion}
                    onClick={() => toggleExclusion(exclusion)}
                  >
                    <span className="chip-check"><Icon name="check" size={13} /></span>
                    {label}
                  </button>
                ))}
              </div>
            </fieldset>
            <label className="field">
              <span className="field-label">Anything else we should know? <span className="optional-label">OPTIONAL</span></span>
              <textarea
                value={draft.circumstances}
                maxLength={1500}
                onChange={(event) =>
                  setDraft((current) => ({
                    ...current,
                    circumstances: event.target.value,
                  }))
                }
                placeholder="Share any circumstances that may shape your plans..."
                rows={4}
              />
              <span className="character-count">{draft.circumstances.length}/1500</span>
            </label>
            <div className="privacy-note">
              <Icon name="shield" size={16} />
              Your answers are used to build this assessment and are stored with its audit record.
            </div>
          </div>
        )}

        {formError && (
          <div className="inline-error" role="alert">
            <Icon name="close" size={16} /> {formError}
          </div>
        )}

        <div className="wizard-actions">
          {step > 0 ? (
            <button
              className="button button-quiet"
              type="button"
              onClick={() => {
                setFormError("");
                setStep((current) => current - 1);
              }}
              disabled={isBusy}
            >
              <Icon name="arrow-left" size={16} /> Back
            </button>
          ) : (
            <span className="muted">Your answers stay private.</span>
          )}
          <button
            className="button button-primary"
            type="button"
            onClick={continueToNext}
            disabled={isBusy}
          >
            {isBusy ? (
              <><span className="spinner" /> Building preview</>
            ) : step === 2 ? (
              <>See my profile <Icon name="arrow-right" size={16} /></>
            ) : (
              <>Continue <Icon name="arrow-right" size={16} /></>
            )}
          </button>
        </div>
      </div>

      <p className="disclaimer-copy">
        This experience is for educational purposes and is not investment advice.
        Recommendations are generated from your answers and the included ETF dataset.
      </p>
    </section>
  );
}

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
  ShareOfLiquidNetWorth,
} from "./types";

export const options = {
  investmentHorizon: [
    ["under 2 years", "Under 2 years"],
    ["2–5", "2–5 years"],
    ["5–10", "5–10 years"],
    ["10+", "10+ years"],
  ] as [InvestmentHorizon, string][],
  emergencyFund: [
    ["none", "None"],
    ["under 3 months", "Under 3 months"],
    ["3–6 months", "3–6 months"],
    ["6+ months of expenses", "6+ months"],
  ] as [EmergencyFund, string][],
  incomeStability: [
    ["salaried", "Salaried"],
    ["variable or commission", "Variable or commission"],
    ["self-employed", "Self-employed"],
    ["no earned income", "No earned income"],
  ] as [IncomeStability, string][],
  shareOfLiquidNetWorth: [
    ["under 10%", "Under 10%"],
    ["10–25%", "10–25%"],
    ["25–50%", "25–50%"],
    ["over 50%", "Over 50%"],
  ] as [ShareOfLiquidNetWorth, string][],
  primaryGoal: [
    ["capital preservation", "Capital preservation"],
    ["income", "Income"],
    ["balanced growth", "Balanced growth"],
    ["aggressive growth", "Aggressive growth"],
  ] as [PrimaryGoal, string][],
  drawdownReaction: [
    ["sell everything", "Sell everything"],
    ["sell some", "Sell some"],
    ["hold", "Hold"],
    ["buy more", "Buy more"],
  ] as [DrawdownReaction, string][],
  maxLoss: [
    ["0%", "0%"],
    ["−5%", "−5%"],
    ["−15%", "−15%"],
    ["−30% or more", "−30% or more"],
  ] as [MaxAcceptableLoss, string][],
  experience: [
    ["none", "None"],
    ["funds only", "Funds only"],
    ["individual stocks and ETFs", "Individual stocks and ETFs"],
    ["derivatives or leverage", "Derivatives or leverage"],
  ] as [InvestmentExperience, string][],
  currency: [
    ["USD", "USD · US Dollar"],
    ["AED", "AED · UAE Dirham"],
    ["EUR", "EUR · Euro"],
    ["GBP", "GBP · Pound Sterling"],
  ] as [BaseCurrency, string][],
  exclusions: [
    ["no crypto", "Exclude crypto"],
    ["sharia-compliant only", "Sharia-compliant only"],
    ["ESG preference", "Prefer ESG funds"],
  ] as [Exclusion, string][],
} as const;

export const preferenceCards = [
  {
    value: "A" as PortfolioPreference,
    label: "Steady",
    returnText: "5% a year",
    fallText: "−19% worst fall",
    mix: "20 / 80 stock–bond",
  },
  {
    value: "B" as PortfolioPreference,
    label: "Balanced",
    returnText: "10% a year",
    fallText: "−22% worst fall",
    mix: "60 / 40 stock–bond",
  },
  {
    value: "C" as PortfolioPreference,
    label: "Growth",
    returnText: "15% a year",
    fallText: "−32% worst fall",
    mix: "90 / 10 stock–bond",
  },
];

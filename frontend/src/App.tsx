import { useCallback, useEffect, useState } from "react";
import {
  createAssessment,
  getRecord,
  listRecords,
  previewAssessment,
} from "./api";
import { HistoryView } from "./components/HistoryView";
import { Icon } from "./components/Icon";
import { NaturalLanguageView } from "./components/NaturalLanguageView";
import { Questionnaire } from "./components/Questionnaire";
import { RecommendationView } from "./components/RecommendationView";
import type {
  AssessmentPreview,
  AssessmentRecord,
  QuestionnaireSubmission,
  RecordVerification,
} from "./types";

type Page = "assessment" | "natural" | "history";

const navigation: { id: Page; label: string; icon: "home" | "sparkles" | "history" }[] = [
  { id: "assessment", label: "Risk assessment", icon: "home" },
  { id: "natural", label: "Explore by intent", icon: "sparkles" },
  { id: "history", label: "Saved records", icon: "history" },
];

function getInitialTheme(): "light" | "dark" {
  try {
    const saved = localStorage.getItem("cognium-theme");
    if (saved === "light" || saved === "dark") return saved;
  } catch {
    // Use the operating system preference when browser storage is unavailable.
  }
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export default function App() {
  const [page, setPage] = useState<Page>("assessment");
  const [formVersion, setFormVersion] = useState(0);
  const [theme, setTheme] = useState<"light" | "dark">(getInitialTheme);
  const [preview, setPreview] = useState<AssessmentPreview | null>(null);
  const [submission, setSubmission] = useState<QuestionnaireSubmission | null>(null);
  const [savedRecord, setSavedRecord] = useState<AssessmentRecord | null>(null);
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [pageError, setPageError] = useState("");

  const [records, setRecords] = useState<AssessmentRecord[]>([]);
  const [isLoadingRecords, setIsLoadingRecords] = useState(false);
  const [recordsError, setRecordsError] = useState("");
  const [selectedRecord, setSelectedRecord] = useState<RecordVerification | null>(null);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    try {
      localStorage.setItem("cognium-theme", theme);
    } catch {
      // Theme still works for this tab if storage is unavailable.
    }
  }, [theme]);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [page, Boolean(preview)]);

  const refreshRecords = useCallback(async () => {
    setIsLoadingRecords(true);
    setRecordsError("");
    try {
      setRecords(await listRecords());
    } catch (error) {
      setRecordsError(
        error instanceof Error ? error.message : "Unable to load assessment history.",
      );
    } finally {
      setIsLoadingRecords(false);
    }
  }, []);

  useEffect(() => {
    if (page === "history") void refreshRecords();
  }, [page, refreshRecords]);

  const openRecord = async (recordId: string) => {
    if (!recordId) {
      setSelectedRecord(null);
      return;
    }
    setRecordsError("");
    try {
      setSelectedRecord(await getRecord(recordId));
    } catch (error) {
      setRecordsError(
        error instanceof Error ? error.message : "Unable to verify this record.",
      );
    }
  };

  const runPreview = async (answers: QuestionnaireSubmission) => {
    setPageError("");
    setIsPreviewing(true);
    try {
      const result = await previewAssessment(answers);
      setPreview(result);
      setSubmission(answers);
      setSavedRecord(null);
    } catch (error) {
      setPageError(
        error instanceof Error
          ? error.message
          : "We couldn’t create your preview. Please try again.",
      );
    } finally {
      setIsPreviewing(false);
    }
  };

  const saveAssessment = async () => {
    if (!submission || !preview || savedRecord) return;
    setPageError("");
    setIsSaving(true);
    try {
      const saved = await createAssessment(submission);
      setSavedRecord(saved);
      setPreview({
        assessment: saved.assessment,
        recommendation: saved.recommendation,
      });
    } catch (error) {
      setPageError(
        error instanceof Error
          ? error.message
          : "We couldn’t save your assessment. Please try again.",
      );
    } finally {
      setIsSaving(false);
    }
  };

  const startNewAssessment = () => {
    setPageError("");
    setPreview(null);
    setSubmission(null);
    setSavedRecord(null);
    setFormVersion((current) => current + 1);
    setPage("assessment");
  };

  const title =
    page === "assessment"
      ? preview
        ? "Your profile"
        : "Assessment"
      : page === "natural"
        ? "Explore by intent"
        : "Saved records";

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a href="#" className="brand" onClick={(event) => { event.preventDefault(); startNewAssessment(); }}>
          <span className="brand-mark"><span>C</span></span>
          <span className="brand-word">cognium<span>.</span></span>
        </a>

        <div className="sidebar-caption">YOUR WORKSPACE</div>
        <nav className="side-nav" aria-label="Main navigation">
          {navigation.map((item) => (
            <button
              className={`nav-item ${page === item.id ? "active" : ""}`}
              type="button"
              key={item.id}
              onClick={() => {
                setPageError("");
                setPage(item.id);
              }}
              aria-current={page === item.id ? "page" : undefined}
            >
              <Icon name={item.icon} size={18} />
              <span>{item.label}</span>
              {item.id === "assessment" && !preview && <i className="nav-indicator" />}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-assurance">
            <span><Icon name="shield" size={16} /></span>
            <div><strong>Thoughtfully considered</strong><small>Your goals guide the process.</small></div>
          </div>
          <div className="sidebar-foot">
            <span className="version-dot" /> Educational experience
          </div>
        </div>
      </aside>

      <div className="main-shell">
        <header className="topbar">
          <div className="mobile-brand">
            <span className="brand-mark small"><span>C</span></span>
            <span className="brand-word">cognium<span>.</span></span>
          </div>
          <div className="breadcrumb">
            <span>Workspace</span><span className="breadcrumb-separator">/</span><strong>{title}</strong>
          </div>
          <div className="topbar-actions">
            <span className="secure-label"><Icon name="shield" size={15} /> Private & secure</span>
            <button
              className="theme-toggle"
              type="button"
              aria-label={`Switch to ${theme === "light" ? "dark" : "light"} theme`}
              title={`Switch to ${theme === "light" ? "dark" : "light"} theme`}
              onClick={() => setTheme((current) => current === "light" ? "dark" : "light")}
            >
              <Icon name={theme === "light" ? "moon" : "sun"} size={17} />
            </button>
            <span className="avatar" aria-label="Guest profile">G</span>
          </div>
        </header>

        <nav className="mobile-nav" aria-label="Main navigation">
          {navigation.map((item) => (
            <button
              className={`mobile-nav-item ${page === item.id ? "active" : ""}`}
              type="button"
              key={item.id}
              onClick={() => {
                setPageError("");
                setPage(item.id);
              }}
              aria-current={page === item.id ? "page" : undefined}
            >
              <Icon name={item.icon} size={16} />
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <main className="main-content">
          {pageError && (
            <div className="error-card page-error" role="alert">
              <span className="error-icon"><Icon name="close" /></span>
              <div><strong>We couldn’t complete that step</strong><p>{pageError}</p></div>
              <button className="icon-button" type="button" aria-label="Dismiss error" onClick={() => setPageError("")}><Icon name="close" size={16} /></button>
            </div>
          )}

          {page === "assessment" && (
            <>
              <div className={preview ? "hidden" : ""}>
                <Questionnaire
                  key={formVersion}
                  isBusy={isPreviewing}
                  onPreview={(answers) => void runPreview(answers)}
                />
              </div>
              {preview && submission && (
              <RecommendationView
                result={preview}
                savedRecord={savedRecord}
                isSaving={isSaving}
                onSave={() => void saveAssessment()}
                onNew={startNewAssessment}
                onEdit={() => {
                  setPreview(null);
                  setSavedRecord(null);
                }}
              />
              )}
            </>
          )}

          {page === "natural" && <NaturalLanguageView />}
          {page === "history" && (
            <HistoryView
              records={records}
              selected={selectedRecord}
              isLoading={isLoadingRecords}
              error={recordsError}
              onOpen={(id) => void openRecord(id)}
              onRefresh={() => void refreshRecords()}
            />
          )}
        </main>

        <footer className="main-footer">
          <span>Cognium Risk Profiler</span>
          <span>Investing involves risk, including possible loss of principal.</span>
        </footer>
      </div>
    </div>
  );
}

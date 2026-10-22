import type { AssessmentRecord, RecordVerification } from "../types";
import { Icon } from "./Icon";
import { RecommendationView } from "./RecommendationView";

function profileName(profile: string) {
  return profile
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

export function HistoryView({
  records,
  selected,
  verification,
  isLoading,
  isVerifying,
  error,
  onOpen,
  onVerify,
  onRefresh,
}: {
  records: AssessmentRecord[];
  selected: AssessmentRecord | null;
  verification: RecordVerification | null;
  isLoading: boolean;
  isVerifying: boolean;
  error: string;
  onOpen: (recordId: string) => void;
  onVerify: (recordId: string) => void;
  onRefresh: () => void;
}) {
  const selectedVerification =
    selected?.id === verification?.record.id ? verification : null;

  return (
    <section className="content-column history-column">
      <div className="page-heading">
        <div>
          <p className="eyebrow">YOUR SAVED ASSESSMENTS</p>
          <h1>A clear record of every decision.</h1>
          <p className="page-subtitle">
            Revisit previous profiles and check that each recommendation record remains intact.
          </p>
        </div>
        <button className="button button-outline" type="button" onClick={onRefresh} disabled={isLoading}>
          <Icon name="refresh" size={16} /> Refresh
        </button>
      </div>

      {error && <div className="inline-error" role="alert"><Icon name="close" size={16} /> {error}</div>}

      {selected && (
        <>
          <article className="verification-card">
            <div className="verification-top">
              <span
                className={`verification-icon ${selectedVerification ? (selectedVerification.verified ? "positive" : "negative") : ""}`}
              >
                <Icon
                  name={selectedVerification ? (selectedVerification.verified ? "shield" : "close") : "file"}
                  size={21}
                />
              </span>
              <div>
                <p className="eyebrow">{selectedVerification ? "RECORD INTEGRITY" : "SAVED ASSESSMENT"}</p>
                <h2>
                  {selectedVerification
                    ? selectedVerification.verified
                      ? "Record verified"
                      : "Integrity check needs attention"
                    : "Historical assessment details"}
                </h2>
                <p>
                  {selectedVerification
                    ? selectedVerification.audit_notes
                    : "This is the saved recommendation from this assessment. Verify its integrity to check that its original inputs and scoring details still match the saved hash."}
                </p>
                <p className="verification-explainer">
                  {selectedVerification
                    ? "The check recalculates the SHA-256 hash from the record’s original inputs, profile, scoring engine version, and creation time, then compares it with the saved hash."
                    : "Opening the assessment shows its saved recommendation; it does not run the integrity check."}
                </p>
              </div>
              <button
                className="icon-button"
                type="button"
                aria-label="Close record details"
                onClick={() => onOpen("")}
              >
                <Icon name="close" />
              </button>
            </div>
            <div className="verification-stats">
              <div><span>Record ID</span><strong>{selected.id}</strong></div>
              <div><span>Profile</span><strong>{profileName(selected.assessment.final_profile)}</strong></div>
              <div><span>Created</span><strong>{new Date(selected.created_at).toLocaleString()}</strong></div>
              <div><span>Engine version</span><strong>{selected.scoring_engine_version}</strong></div>
            </div>
            <div className="verification-hash">
              <div>
                <span>STORED INTEGRITY HASH</span>
                <code>{selected.integrity_hash}</code>
              </div>
              <button
                className="button button-outline"
                type="button"
                onClick={() => onVerify(selected.id)}
                disabled={isVerifying}
              >
                <Icon name="shield" size={15} />
                {isVerifying ? "Checking integrity…" : selectedVerification ? "Verify again" : "Verify integrity"}
              </button>
            </div>
          </article>
          <RecommendationView
            result={selected}
            savedRecord={selected}
            isSaving={false}
            onSave={() => {}}
            onEdit={() => {}}
            onNew={() => {}}
            readOnly
          />
        </>
      )}

      <div className="panel history-panel">
        <div className="panel-heading">
          <div>
            <span className="panel-overline">ASSESSMENT RECORDS</span>
            <h3>Your history</h3>
          </div>
          <span className="holdings-count">{records.length} records</span>
        </div>
        {isLoading ? (
          <div className="loading-state"><span className="spinner" /> Loading your records...</div>
        ) : records.length === 0 ? (
          <div className="empty-state compact">
            <span className="empty-icon"><Icon name="file" size={24} /></span>
            <h3>No saved assessments yet</h3>
            <p>Complete an assessment and save it to build your history.</p>
          </div>
        ) : (
          <div className="table-scroll">
            <table>
              <thead><tr><th>Assessment</th><th>Date</th><th>Profile</th><th>Capacity</th><th>Tolerance</th><th /></tr></thead>
              <tbody>
                {records.map((record) => (
                  <tr
                    key={record.id}
                    className="history-row"
                    onClick={() => onOpen(record.id)}
                    onKeyDown={(event) => {
                      if (
                        event.target === event.currentTarget &&
                        (event.key === "Enter" || event.key === " ")
                      ) {
                        event.preventDefault();
                        onOpen(record.id);
                      }
                    }}
                    tabIndex={0}
                  >
                    <td><div className="fund-name"><strong>{record.id}</strong><span>Engine v{record.scoring_engine_version}</span></div></td>
                    <td>{new Date(record.created_at).toLocaleDateString()}</td>
                    <td><span className="profile-pill">{profileName(record.assessment.final_profile)}</span></td>
                    <td>{Math.round(record.assessment.capacity_score)}/100</td>
                    <td>{Math.round(record.assessment.tolerance_score)}/100</td>
                    <td>
                      <button
                        className="link-button"
                        type="button"
                        onClick={(event) => {
                          event.stopPropagation();
                          onVerify(record.id);
                        }}
                        disabled={isVerifying}
                      >
                        {isVerifying ? "Checking…" : "Verify record"} <Icon name="arrow-right" size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}

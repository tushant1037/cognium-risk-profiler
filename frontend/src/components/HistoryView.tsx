import type { AssessmentRecord, RecordVerification } from "../types";
import { Icon } from "./Icon";

function profileName(profile: string) {
  return profile
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

export function HistoryView({
  records,
  selected,
  isLoading,
  error,
  onOpen,
  onRefresh,
}: {
  records: AssessmentRecord[];
  selected: RecordVerification | null;
  isLoading: boolean;
  error: string;
  onOpen: (recordId: string) => void;
  onRefresh: () => void;
}) {
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
        <article className="verification-card">
          <div className="verification-top">
            <span className={`verification-icon ${selected.verified ? "positive" : "negative"}`}>
              <Icon name={selected.verified ? "shield" : "close"} size={21} />
            </span>
            <div>
              <p className="eyebrow">RECORD INTEGRITY</p>
              <h2>{selected.verified ? "Record verified" : "Integrity check needs attention"}</h2>
              <p>{selected.audit_notes}</p>
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
            <div><span>Record ID</span><strong>{selected.record.id}</strong></div>
            <div><span>Profile</span><strong>{profileName(selected.record.assessment.final_profile)}</strong></div>
            <div><span>Created</span><strong>{new Date(selected.record.created_at).toLocaleString()}</strong></div>
            <div><span>Engine version</span><strong>{selected.record.scoring_engine_version}</strong></div>
          </div>
          <div className="verification-hash">
            <span>INTEGRITY HASH</span>
            <code>{selected.record.integrity_hash}</code>
          </div>
        </article>
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
                  <tr key={record.id}>
                    <td><div className="fund-name"><strong>{record.id}</strong><span>Engine v{record.scoring_engine_version}</span></div></td>
                    <td>{new Date(record.created_at).toLocaleDateString()}</td>
                    <td><span className="profile-pill">{profileName(record.assessment.final_profile)}</span></td>
                    <td>{Math.round(record.assessment.capacity_score)}/100</td>
                    <td>{Math.round(record.assessment.tolerance_score)}/100</td>
                    <td>
                      <button className="link-button" type="button" onClick={() => onOpen(record.id)}>
                        Verify record <Icon name="arrow-right" size={14} />
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

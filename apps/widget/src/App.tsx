import {
  AlertTriangle,
  BookOpen,
  Braces,
  CheckCircle2,
  ChevronRight,
  CircleAlert,
  ClipboardList,
  Code2,
  Eye,
  FileText,
  GitBranch,
  Layers,
  ListChecks,
  Loader2,
  MessageSquareText,
  Network,
  PanelLeft,
  RotateCcw,
  Search,
  Table2,
  Workflow,
  ZoomIn,
  ZoomOut,
  type LucideIcon,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { useCallTool } from "./hooks/use_call_tool.js";
import { useToolResult } from "./hooks/use_tool_result.js";
import { useWidgetState } from "./hooks/use_widget_state.js";
import { notifyIntrinsicHeight, sendFollowUpMessage, updateModelContext } from "./lib/openai_bridge.js";
import {
  auditFromResult,
  buildFindingPrompt,
  contextFromResult,
  findingCountBySeverity,
  formatJson,
  isViewKey,
  mergeWorkspaceData,
  metadataText,
  methodTone,
  sanitizeSvg,
  statusLabel,
  traceabilityRows,
  workspaceFromToolResult,
} from "./lib/review_data.js";
import type {
  DiagramStep,
  FeatureAuditResult,
  FeatureContext,
  FeatureDiagram,
  FeatureSummary,
  OpenApiOperationSlice,
  ProductDoc,
  ReviewWorkspaceData,
  RuleFinding,
  TestIdea,
  ViewKey,
  WidgetState,
} from "./types.js";

const defaultWidgetState: WidgetState = {
  activeView: "features",
  showDiagramSource: false,
  diagramZoom: 1,
  diagramPan: { x: 0, y: 0 },
};

const views: Array<{ key: ViewKey; label: string; icon: LucideIcon }> = [
  { key: "features", label: "Features", icon: PanelLeft },
  { key: "overview", label: "Overview", icon: Layers },
  { key: "docs", label: "Docs", icon: BookOpen },
  { key: "openapi", label: "OpenAPI", icon: Table2 },
  { key: "diagram", label: "Diagram", icon: Workflow },
  { key: "incidents", label: "Incidents", icon: CircleAlert },
  { key: "consistency", label: "Consistency", icon: AlertTriangle },
  { key: "test_gaps", label: "Test gaps", icon: ListChecks },
  { key: "traceability", label: "Traceability", icon: GitBranch },
  { key: "source", label: "Source", icon: Code2 },
];

export function App() {
  const toolResult = useToolResult();
  const incomingWorkspace = useMemo(() => workspaceFromToolResult(toolResult), [toolResult]);
  const [workspace, setWorkspace] = useState<ReviewWorkspaceData>(() => incomingWorkspace);
  const [widgetState, setWidgetState] = useWidgetState<WidgetState>(defaultWidgetState);
  const { callTool, loadingTool, error, clearError } = useCallTool();
  const [manualError, setManualError] = useState<string | null>(null);

  useEffect(() => {
    if (!toolResult) return;
    setWorkspace((current) => mergeWorkspaceData(current, incomingWorkspace));
    const requestedView = incomingWorkspace.workspace?.view;
    if (isViewKey(requestedView)) {
      setWidgetState((current) => ({ ...current, activeView: requestedView }));
    }
  }, [incomingWorkspace, setWidgetState, toolResult]);

  useEffect(() => {
    const selectedFeatureId = workspace.context?.feature_id ?? workspace.features[0]?.feature_id;
    if (!selectedFeatureId || widgetState.selectedFeatureId) return;
    setWidgetState((current) => ({
      ...current,
      selectedFeatureId,
    }));
  }, [setWidgetState, widgetState.selectedFeatureId, workspace.context?.feature_id, workspace.features]);

  useEffect(() => {
    notifyIntrinsicHeight();
  }, [workspace, widgetState, loadingTool, error, manualError]);

  const selectedFeatureId = widgetState.selectedFeatureId ?? workspace.context?.feature_id;
  const selectedFeature = workspace.features.find((feature) => feature.feature_id === selectedFeatureId);
  const context = workspace.context?.feature_id === selectedFeatureId ? workspace.context : undefined;
  const audit = workspace.audit?.feature_id === selectedFeatureId ? workspace.audit : undefined;
  const activeView = widgetState.activeView;
  const selectedOperationId =
    widgetState.selectedOperationId ?? context?.openapi_operations[0]?.operation_id;
  const selectedDiagram = context?.diagrams[0];

  async function loadFeature(featureId: string, view: ViewKey = activeView) {
    setManualError(null);
    clearError();
    setWidgetState((current) => ({
      ...current,
      selectedFeatureId: featureId,
      activeView: view,
      selectedOperationId: undefined,
      selectedStepId: undefined,
      selectedFindingId: undefined,
    }));

    try {
      const [contextResult, auditResult] = await Promise.all([
        callTool("get_feature_context", { feature_id: featureId }),
        callTool("audit_feature_consistency", { feature_id: featureId }),
      ]);
      const nextContext = contextFromResult(contextResult);
      const nextAudit = auditFromResult(auditResult);
      setWorkspace((current) => ({
        ...current,
        context: nextContext ?? current.context,
        audit: nextAudit ?? current.audit,
        workspace: current.workspace
          ? {
              ...current.workspace,
              view,
              feature_id: featureId,
              feature_title: nextContext?.title ?? current.workspace.feature_title,
              finding_count: nextAudit?.findings.length ?? current.workspace.finding_count,
              status: nextAudit?.overall_status ?? current.workspace.status,
            }
          : current.workspace,
      }));
    } catch (cause) {
      setManualError(cause instanceof Error ? cause.message : "Feature context failed to load.");
    }
  }

  function setActiveView(view: ViewKey) {
    setWidgetState((current) => ({ ...current, activeView: view }));
  }

  function selectOperation(operationId: string) {
    setWidgetState((current) => ({ ...current, selectedOperationId: operationId }));
  }

  function selectStep(step: DiagramStep) {
    setWidgetState((current) => ({
      ...current,
      selectedStepId: step.step_id,
      selectedOperationId: step.related_operation_id ?? current.selectedOperationId,
    }));
  }

  async function askAboutFinding(finding: RuleFinding) {
    const prompt = buildFindingPrompt(finding, context);
    setWidgetState((current) => ({ ...current, selectedFindingId: finding.finding_id }));
    await updateModelContext(`Selected finding: ${finding.title}`, {
      finding_id: finding.finding_id,
      feature_id: context?.feature_id,
      severity: finding.severity,
      affected_operation_ids: finding.affected_operation_ids,
    });
    await sendFollowUpMessage(prompt);
  }

  return (
    <div className="app-shell">
      <aside className="feature-rail">
        <div className="rail-header">
          <div>
            <h1>Feature Review</h1>
            <p>{workspace.features.length} features</p>
          </div>
          {loadingTool ? <Loader2 className="spin" size={18} aria-label="Loading" /> : null}
        </div>
        <FeatureList
          features={workspace.features}
          selectedFeatureId={selectedFeatureId}
          onSelect={(featureId) => void loadFeature(featureId, "overview")}
        />
      </aside>

      <main className="workspace">
        <header className="workspace-header">
          <div>
            <div className="eyebrow">{context?.domain ?? selectedFeature?.domain ?? "Review"}</div>
            <h2>{context?.title ?? selectedFeature?.title ?? "Feature Review Workspace"}</h2>
          </div>
          <div className={`status-pill status-${audit?.overall_status ?? selectedFeature?.review_status ?? "not_reviewed"}`}>
            {statusIcon(audit?.overall_status ?? selectedFeature?.review_status)}
            {statusLabel(audit?.overall_status ?? selectedFeature?.review_status)}
          </div>
        </header>

        <nav className="tabs" aria-label="Workspace views">
          {views.map((view) => {
            const Icon = view.icon;
            return (
              <button
                className={activeView === view.key ? "tab active" : "tab"}
                key={view.key}
                onClick={() => setActiveView(view.key)}
                type="button"
              >
                <Icon size={16} />
                <span>{view.label}</span>
              </button>
            );
          })}
        </nav>

        {error || manualError ? (
          <div className="error-strip">
            <AlertTriangle size={16} />
            <span>{manualError ?? error}</span>
          </div>
        ) : null}

        <section className="view-surface">
          {activeView === "features" ? (
            <FeaturesView features={workspace.features} selectedFeatureId={selectedFeatureId} onSelect={loadFeature} />
          ) : null}
          {activeView === "overview" ? (
            <OverviewView context={context} audit={audit} feature={selectedFeature} onAsk={askAboutFinding} />
          ) : null}
          {activeView === "docs" ? <DocsView context={context} /> : null}
          {activeView === "openapi" ? (
            <OpenApiView context={context} selectedOperationId={selectedOperationId} onSelectOperation={selectOperation} />
          ) : null}
          {activeView === "diagram" ? (
            <DiagramView
              audit={audit}
              diagram={selectedDiagram}
              selectedOperationId={selectedOperationId}
              selectedStepId={widgetState.selectedStepId}
              showSource={widgetState.showDiagramSource}
              zoom={widgetState.diagramZoom}
              pan={widgetState.diagramPan}
              onSelectStep={selectStep}
              onSelectOperation={selectOperation}
              onSetShowSource={(showDiagramSource) =>
                setWidgetState((current) => ({ ...current, showDiagramSource }))
              }
              onSetViewport={(diagramZoom, diagramPan) =>
                setWidgetState((current) => ({ ...current, diagramZoom, diagramPan }))
              }
            />
          ) : null}
          {activeView === "incidents" ? <IncidentsView context={context} /> : null}
          {activeView === "consistency" ? (
            <ConsistencyView audit={audit} selectedFindingId={widgetState.selectedFindingId} onAsk={askAboutFinding} />
          ) : null}
          {activeView === "test_gaps" ? <TestGapsView audit={audit} /> : null}
          {activeView === "traceability" ? <TraceabilityView context={context} audit={audit} /> : null}
          {activeView === "source" ? <SourceView context={context} /> : null}
        </section>
      </main>
    </div>
  );
}

function FeatureList({
  features,
  selectedFeatureId,
  onSelect,
}: {
  features: FeatureSummary[];
  selectedFeatureId?: string;
  onSelect: (featureId: string) => void;
}) {
  if (features.length === 0) {
    return <EmptyState title="No features" detail="The render payload did not include feature summaries." />;
  }
  return (
    <div className="feature-list">
      {features.map((feature) => (
        <button
          className={feature.feature_id === selectedFeatureId ? "feature-row active" : "feature-row"}
          key={feature.feature_id}
          onClick={() => onSelect(feature.feature_id)}
          type="button"
        >
          <span className="feature-title">{feature.title}</span>
          <span className="feature-domain">{feature.domain}</span>
          <span className="feature-metrics">
            <span>{feature.related_operations_count} ops</span>
            <span>{feature.diagram_count} diagrams</span>
            <span>{feature.incident_count} incidents</span>
          </span>
        </button>
      ))}
    </div>
  );
}

function FeaturesView({
  features,
  selectedFeatureId,
  onSelect,
}: {
  features: FeatureSummary[];
  selectedFeatureId?: string;
  onSelect: (featureId: string, view?: ViewKey) => Promise<void>;
}) {
  if (features.length === 0) return <EmptyState title="No features" detail="No manifest entries were returned." />;
  return (
    <div className="feature-grid">
      {features.map((feature) => (
        <button
          className={feature.feature_id === selectedFeatureId ? "feature-card active" : "feature-card"}
          key={feature.feature_id}
          onClick={() => void onSelect(feature.feature_id, "overview")}
          type="button"
        >
          <span className="feature-card-top">
            <span className="feature-card-title">{feature.title}</span>
            <ChevronRight size={17} />
          </span>
          <span className="feature-card-domain">{feature.domain}</span>
          <span className="metric-row">
            <span><Network size={14} />{feature.related_operations_count} operations</span>
            <span><Workflow size={14} />{feature.diagram_count} diagrams</span>
            <span><CircleAlert size={14} />{feature.incident_count} incidents</span>
          </span>
        </button>
      ))}
    </div>
  );
}

function OverviewView({
  context,
  audit,
  feature,
  onAsk,
}: {
  context?: FeatureContext;
  audit?: FeatureAuditResult;
  feature?: FeatureSummary;
  onAsk: (finding: RuleFinding) => Promise<void>;
}) {
  if (!context && !feature) return <EmptyState title="No feature selected" detail="Feature context is empty." />;
  const severityCounts = findingCountBySeverity(audit?.findings ?? []);
  return (
    <div className="stack">
      <div className="summary-strip">
        <Metric label="Operations" value={context?.openapi_operations.length ?? feature?.related_operations_count ?? 0} icon={Network} />
        <Metric label="Diagrams" value={context?.diagrams.length ?? feature?.diagram_count ?? 0} icon={Workflow} />
        <Metric label="Incidents" value={context?.incidents.length ?? feature?.incident_count ?? 0} icon={CircleAlert} />
        <Metric label="Findings" value={audit?.findings.length ?? 0} icon={ClipboardList} />
      </div>
      <div className="overview-grid">
        <section className="panel">
          <h3>Review status</h3>
          <div className="status-breakdown">
            <span className="severity high">High {severityCounts.high}</span>
            <span className="severity medium">Medium {severityCounts.medium}</span>
            <span className="severity low">Low {severityCounts.low}</span>
          </div>
          <p>{audit?.model_context_hint ?? "No model context hint was returned."}</p>
        </section>
        <section className="panel">
          <h3>Next actions</h3>
          {audit?.recommended_next_actions.length ? (
            <ul className="plain-list">
              {audit.recommended_next_actions.map((action) => (
                <li key={action}>{action}</li>
              ))}
            </ul>
          ) : (
            <p>No next actions.</p>
          )}
        </section>
      </div>
      <section className="panel">
        <h3>Top findings</h3>
        <FindingList findings={(audit?.findings ?? []).slice(0, 4)} onAsk={onAsk} />
      </section>
    </div>
  );
}

function DocsView({ context }: { context?: FeatureContext }) {
  if (!context) return <EmptyState title="No docs" detail="Feature context has not been loaded." />;
  return (
    <div className="docs-layout">
      <DocPanel title="User story" doc={context.user_story} />
      {context.acceptance_criteria ? (
        <DocPanel title="Acceptance criteria" doc={context.acceptance_criteria} />
      ) : (
        <EmptyState title="No acceptance criteria" detail="No linked acceptance criteria document." />
      )}
      <section className="panel full-span">
        <h3>Product rules</h3>
        <div className="rule-grid">
          <RuleItem label="Status" value={context.acceptance_criteria?.status ?? context.user_story.status} />
          <RuleItem label="Version" value={context.acceptance_criteria?.version ?? context.user_story.version} />
          <RuleItem label="Related operations" value={context.user_story.related_openapi_operations.join(", ") || "None"} />
          <RuleItem label="Related diagrams" value={context.user_story.related_diagrams?.join(", ") || "None"} />
        </div>
      </section>
    </div>
  );
}

function OpenApiView({
  context,
  selectedOperationId,
  onSelectOperation,
}: {
  context?: FeatureContext;
  selectedOperationId?: string;
  onSelectOperation: (operationId: string) => void;
}) {
  if (!context) return <EmptyState title="No OpenAPI data" detail="Feature context has not been loaded." />;
  const selected = context.openapi_operations.find((operation) => operation.operation_id === selectedOperationId)
    ?? context.openapi_operations[0];
  return (
    <div className="split-view">
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Method</th>
              <th>Path</th>
              <th>Operation</th>
              <th>Schemas</th>
            </tr>
          </thead>
          <tbody>
            {context.openapi_operations.map((operation) => (
              <tr
                className={operation.operation_id === selected?.operation_id ? "selected" : ""}
                key={operation.operation_id}
                onClick={() => onSelectOperation(operation.operation_id)}
              >
                <td><span className={`method ${methodTone(operation.method)}`}>{operation.method}</span></td>
                <td><code>{operation.path}</code></td>
                <td>{operation.operation_id}</td>
                <td>{operation.related_schema_names.join(", ") || "None"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {selected ? (
        <section className="panel detail-panel">
          <h3>{selected.summary ?? selected.operation_id}</h3>
          <p>{selected.description ?? "No operation description."}</p>
          <DataBlock title="Parameters" value={selected.parameters} />
          <DataBlock title="Request body" value={selected.request_body} />
          <DataBlock title="Responses" value={selected.responses} />
          <DataBlock title="Security" value={selected.security} />
        </section>
      ) : null}
    </div>
  );
}

function DiagramView({
  audit,
  diagram,
  selectedOperationId,
  selectedStepId,
  showSource,
  zoom,
  pan,
  onSelectStep,
  onSelectOperation,
  onSetShowSource,
  onSetViewport,
}: {
  audit?: FeatureAuditResult;
  diagram?: FeatureDiagram;
  selectedOperationId?: string;
  selectedStepId?: string;
  showSource: boolean;
  zoom: number;
  pan: { x: number; y: number };
  onSelectStep: (step: DiagramStep) => void;
  onSelectOperation: (operationId: string) => void;
  onSetShowSource: (showSource: boolean) => void;
  onSetViewport: (zoom: number, pan: { x: number; y: number }) => void;
}) {
  if (!diagram) return <EmptyState title="No diagram" detail="No PlantUML diagram is linked to this feature." />;
  const driftFindings = (audit?.findings ?? []).filter((finding) =>
    finding.category.includes("diagram") || finding.category.includes("operation"),
  );
  return (
    <div className="diagram-layout">
      <DiagramCanvas
        diagram={diagram}
        showSource={showSource}
        zoom={zoom}
        pan={pan}
        onSetShowSource={onSetShowSource}
        onSetViewport={onSetViewport}
      />
      <aside className="side-panel">
        <DiagramStepList
          steps={diagram.steps}
          selectedStepId={selectedStepId}
          selectedOperationId={selectedOperationId}
          onSelectStep={onSelectStep}
          onSelectOperation={onSelectOperation}
        />
        {driftFindings.length ? (
          <section className="panel compact">
            <h3>Diagram/API drift</h3>
            <FindingList findings={driftFindings} />
          </section>
        ) : (
          <section className="panel compact">
            <h3>Diagram/API drift</h3>
            <p>No drift findings.</p>
          </section>
        )}
      </aside>
    </div>
  );
}

function DiagramCanvas({
  diagram,
  showSource,
  zoom,
  pan,
  onSetShowSource,
  onSetViewport,
}: {
  diagram: FeatureDiagram;
  showSource: boolean;
  zoom: number;
  pan: { x: number; y: number };
  onSetShowSource: (showSource: boolean) => void;
  onSetViewport: (zoom: number, pan: { x: number; y: number }) => void;
}) {
  const dragStart = useRef<{ x: number; y: number; pan: { x: number; y: number } } | null>(null);
  const svg = diagram.rendered_svg ? sanitizeSvg(diagram.rendered_svg) : "";

  function clampZoom(nextZoom: number) {
    return Math.min(2.5, Math.max(0.55, Number(nextZoom.toFixed(2))));
  }

  return (
    <section className="diagram-canvas">
      <div className="canvas-toolbar">
        <div>
          <h3>{diagram.title}</h3>
          <p>{diagram.related_operation_ids.join(", ") || "No operation markers"}</p>
        </div>
        <div className="icon-actions">
          <button title="Zoom out" type="button" onClick={() => onSetViewport(clampZoom(zoom - 0.15), pan)}>
            <ZoomOut size={16} />
          </button>
          <button title="Zoom in" type="button" onClick={() => onSetViewport(clampZoom(zoom + 0.15), pan)}>
            <ZoomIn size={16} />
          </button>
          <button title="Reset view" type="button" onClick={() => onSetViewport(1, { x: 0, y: 0 })}>
            <RotateCcw size={16} />
          </button>
          <button
            className={showSource ? "active" : ""}
            title="Toggle source"
            type="button"
            onClick={() => onSetShowSource(!showSource)}
          >
            {showSource ? <Eye size={16} /> : <Code2 size={16} />}
          </button>
        </div>
      </div>
      {showSource ? (
        <pre className="source-block">{diagram.source}</pre>
      ) : (
        <div
          className="svg-stage"
          onPointerDown={(event) => {
            dragStart.current = { x: event.clientX, y: event.clientY, pan };
            event.currentTarget.setPointerCapture(event.pointerId);
          }}
          onPointerMove={(event) => {
            if (!dragStart.current) return;
            const dx = event.clientX - dragStart.current.x;
            const dy = event.clientY - dragStart.current.y;
            onSetViewport(zoom, {
              x: dragStart.current.pan.x + dx,
              y: dragStart.current.pan.y + dy,
            });
          }}
          onPointerUp={() => {
            dragStart.current = null;
          }}
        >
          {svg ? (
            <div
              className="svg-frame"
              style={{ transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})` }}
              dangerouslySetInnerHTML={{ __html: svg }}
            />
          ) : (
            <EmptyState title="No SVG" detail="The diagram source is available in Source view." />
          )}
        </div>
      )}
    </section>
  );
}

function DiagramStepList({
  steps,
  selectedStepId,
  selectedOperationId,
  onSelectStep,
  onSelectOperation,
}: {
  steps: DiagramStep[];
  selectedStepId?: string;
  selectedOperationId?: string;
  onSelectStep: (step: DiagramStep) => void;
  onSelectOperation: (operationId: string) => void;
}) {
  return (
    <section className="panel compact">
      <h3>Steps</h3>
      <div className="step-list">
        {steps.map((step) => (
          <button
            className={step.step_id === selectedStepId ? "step-row active" : "step-row"}
            key={step.step_id}
            onClick={() => onSelectStep(step)}
            type="button"
          >
            <span className="step-id">{step.step_id}</span>
            <span className="step-label">{step.label}</span>
            {step.related_operation_id ? (
              <span
                className={step.related_operation_id === selectedOperationId ? "operation-chip active" : "operation-chip"}
                onClick={(event) => {
                  event.stopPropagation();
                  onSelectOperation(step.related_operation_id as string);
                }}
              >
                {step.related_operation_id}
              </span>
            ) : null}
          </button>
        ))}
      </div>
    </section>
  );
}

function IncidentsView({ context }: { context?: FeatureContext }) {
  if (!context) return <EmptyState title="No incidents" detail="Feature context has not been loaded." />;
  if (context.incidents.length === 0) return <EmptyState title="No incidents" detail="No incident notes are linked." />;
  return (
    <div className="card-list">
      {context.incidents.map((incident) => (
        <article className="item-card" key={incident.document_id}>
          <div className="item-card-header">
            <div>
              <h3>{incident.title}</h3>
              <p>{incident.document_id} · {incident.status} · v{incident.version}</p>
            </div>
            <span className="operation-chip">{incident.related_openapi_operations.join(", ") || "No ops"}</span>
          </div>
          <p>{incident.text}</p>
          <div className="rule-grid">
            <RuleItem label="Affected operations" value={incident.related_openapi_operations.join(", ") || "None"} />
            <RuleItem label="Suspected root cause" value={metadataText(incident, "suspected_root_cause")} />
            <RuleItem label="Resolution" value={metadataText(incident, "resolution")} />
          </div>
        </article>
      ))}
    </div>
  );
}

function ConsistencyView({
  audit,
  selectedFindingId,
  onAsk,
}: {
  audit?: FeatureAuditResult;
  selectedFindingId?: string;
  onAsk: (finding: RuleFinding) => Promise<void>;
}) {
  if (!audit) return <EmptyState title="No findings" detail="Audit results have not been loaded." />;
  return (
    <div className="stack">
      <section className="panel">
        <h3>Deterministic findings</h3>
        <FindingList findings={audit.findings} selectedFindingId={selectedFindingId} onAsk={onAsk} />
      </section>
    </div>
  );
}

function TestGapsView({ audit }: { audit?: FeatureAuditResult }) {
  if (!audit) return <EmptyState title="No test gaps" detail="Audit results have not been loaded." />;
  return (
    <div className="stack">
      <section className="panel">
        <h3>Generated test ideas</h3>
        <TestIdeaList testIdeas={audit.generated_test_ideas} />
      </section>
      <section className="panel">
        <h3>Missing-test findings</h3>
        <FindingList findings={audit.findings.filter((finding) => finding.category.includes("test"))} />
      </section>
    </div>
  );
}

function TraceabilityView({ context, audit }: { context?: FeatureContext; audit?: FeatureAuditResult }) {
  const rows = traceabilityRows(context, audit);
  if (!context) return <EmptyState title="No traceability" detail="Feature context has not been loaded." />;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>User story</th>
            <th>AC</th>
            <th>Diagram step</th>
            <th>Operation</th>
            <th>Incident</th>
            <th>Test idea</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.operationId}>
              <td>{row.userStory}</td>
              <td>{row.acceptanceCriteria}</td>
              <td>{row.diagramStep}</td>
              <td><code>{row.operationId}</code></td>
              <td>{row.incident}</td>
              <td>{row.testIdea}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function SourceView({ context }: { context?: FeatureContext }) {
  if (!context) return <EmptyState title="No source" detail="Feature context has not been loaded." />;
  return (
    <div className="source-grid">
      <SourcePanel title="User story markdown" value={context.user_story.text} />
      {context.acceptance_criteria ? (
        <SourcePanel title="Acceptance criteria markdown" value={context.acceptance_criteria.text} />
      ) : null}
      {context.diagrams.map((diagram) => (
        <SourcePanel key={diagram.diagram_id} title={`${diagram.title} PlantUML`} value={diagram.source} />
      ))}
      {context.openapi_operations.map((operation) => (
        <SourcePanel key={operation.operation_id} title={`${operation.operation_id} OpenAPI slice`} value={formatJson(operation)} />
      ))}
    </div>
  );
}

function DocPanel({ title, doc }: { title: string; doc: ProductDoc }) {
  return (
    <article className="panel doc-panel">
      <div className="doc-heading">
        <FileText size={17} />
        <div>
          <h3>{title}</h3>
          <p>{doc.document_id} · {doc.status} · v{doc.version}</p>
        </div>
      </div>
      <p>{doc.text}</p>
      <div className="doc-links">
        {doc.related_openapi_operations.map((operationId) => (
          <span className="operation-chip" key={operationId}>{operationId}</span>
        ))}
      </div>
    </article>
  );
}

function FindingList({
  findings,
  selectedFindingId,
  onAsk,
}: {
  findings: RuleFinding[];
  selectedFindingId?: string;
  onAsk?: (finding: RuleFinding) => Promise<void>;
}) {
  if (findings.length === 0) return <EmptyState title="No findings" detail="No findings in this view." />;
  return (
    <div className="finding-list">
      {findings.map((finding) => (
        <article
          className={finding.finding_id === selectedFindingId ? "finding-card active" : "finding-card"}
          key={finding.finding_id}
        >
          <div className="finding-topline">
            <span className={`severity ${finding.severity}`}>{finding.severity}</span>
            <span>{finding.category}</span>
          </div>
          <h4>{finding.title}</h4>
          <p>{finding.description}</p>
          <div className="evidence-row">
            {finding.evidence_refs.map((ref) => <code key={ref}>{ref}</code>)}
            {finding.affected_operation_ids.map((operationId) => <span className="operation-chip" key={operationId}>{operationId}</span>)}
          </div>
          <div className="finding-action-row">
            <span>{finding.recommended_action}</span>
            {onAsk ? (
              <button type="button" className="ghost-action" onClick={() => void onAsk(finding)}>
                <MessageSquareText size={15} />
                Ask ChatGPT
              </button>
            ) : null}
          </div>
        </article>
      ))}
    </div>
  );
}

function TestIdeaList({ testIdeas }: { testIdeas: TestIdea[] }) {
  if (testIdeas.length === 0) return <EmptyState title="No test ideas" detail="No generated tests were returned." />;
  return (
    <div className="card-list">
      {testIdeas.map((testIdea) => (
        <article className="item-card" key={testIdea.test_id}>
          <div className="item-card-header">
            <div>
              <h3>{testIdea.title}</h3>
              <p>{testIdea.test_id} · {testIdea.type}</p>
            </div>
            <span className="operation-chip">{testIdea.related_operation_ids.join(", ") || "No ops"}</span>
          </div>
          <p>{testIdea.given_when_then}</p>
          <p className="muted">{testIdea.rationale}</p>
        </article>
      ))}
    </div>
  );
}

function Metric({ label, value, icon: Icon }: { label: string; value: number; icon: LucideIcon }) {
  return (
    <div className="metric">
      <Icon size={18} />
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function RuleItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rule-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function DataBlock({ title, value }: { title: string; value: unknown }) {
  return (
    <details className="data-block">
      <summary><Braces size={15} />{title}</summary>
      <pre>{formatJson(value)}</pre>
    </details>
  );
}

function SourcePanel({ title, value }: { title: string; value: string }) {
  return (
    <section className="panel">
      <h3>{title}</h3>
      <pre className="source-block">{value}</pre>
    </section>
  );
}

function EmptyState({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="empty-state">
      <Search size={20} />
      <h3>{title}</h3>
      <p>{detail}</p>
    </div>
  );
}

function statusIcon(status?: string) {
  if (status === "passed") return <CheckCircle2 size={16} />;
  if (status === "failed") return <AlertTriangle size={16} />;
  return <CircleAlert size={16} />;
}

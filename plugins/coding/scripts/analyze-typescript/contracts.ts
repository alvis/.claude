/** selected scope and optional lint eligibility configuration */
export interface AnalysisOptions {
  readonly files: readonly string[];
  readonly repositoryRoot?: string;
  readonly profilePath?: string;
}

/** source coordinates use absolute paths and one-based line and column numbers */
export interface Location {
  readonly file: string;
  readonly line: number;
  readonly column: number;
}

/** an eligible anonymous type occurrence */
export interface Occurrence extends Location {
  readonly selected: boolean;
  readonly text: string;
}

/** existing declaration requiring semantic and import-direction review */
export interface SharedContract extends Location {
  readonly name: string;
  readonly type_arguments: readonly string[];
}

/** matching occurrences and existing contracts within a package */
export interface TypeGroup {
  readonly rule_id: "TYP-TYPE-09";
  readonly package_root: string;
  readonly occurrences: readonly Occurrence[];
  readonly candidates: readonly SharedContract[];
}

/** an unsupported or uncertain documented error, requiring human review */
export interface ErrorCandidate extends Location {
  readonly rule_id: "DOC-CONT-06";
  readonly function_name: string;
  readonly documented_error: string;
  readonly reason: "unsupported" | "unresolved";
  readonly message: string;
}

/** analysis failures and uncertainties are separate from advisory findings */
export interface Diagnostic {
  readonly kind: "failure" | "review";
  readonly message: string;
  readonly file?: string;
  readonly line?: number;
  readonly column?: number;
}

/** package coverage records exactly which files were counted */
export interface PackageScope {
  readonly root: string;
  readonly files: readonly string[];
  readonly selected_files: readonly string[];
}

/** deterministic advisory output; failures must never be treated as a clean scan */
export interface AnalysisReport {
  readonly status: "complete" | "failure";
  readonly packages: readonly PackageScope[];
  readonly reuse_candidates: readonly TypeGroup[];
  readonly extraction_proposals: readonly TypeGroup[];
  readonly error_documentation_candidates: readonly ErrorCandidate[];
  readonly diagnostics: readonly Diagnostic[];
}

/** package parser input retains repository boundaries for compiler configuration */
export interface PackageRequest extends PackageScope {
  readonly repository_root: string;
}

/** one package's findings before report aggregation */
export interface PackageAnalysis {
  readonly reuse_candidates: readonly TypeGroup[];
  readonly extraction_proposals: readonly TypeGroup[];
  readonly error_documentation_candidates: readonly ErrorCandidate[];
  readonly diagnostics: readonly Diagnostic[];
}

/** lazily loaded parser capability */
export interface ParserModule {
  readonly analyzePackage: (request: PackageRequest) => PackageAnalysis;
}

/** parser loading can be supplied by embedding callers */
export interface AnalysisDependencies {
  readonly loadParser?: () => Promise<ParserModule>;
}

/** CLI output destinations default to process streams */
export interface OutputSinks {
  readonly stdout?: (text: string) => void;
  readonly stderr?: (text: string) => void;
}

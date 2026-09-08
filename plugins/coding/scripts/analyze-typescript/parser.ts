import { dirname } from "node:path";

import { Project, ts } from "ts-morph@28";

import { nearestFile } from "./discovery.ts";
import { findErrorDocumentation } from "./errors.ts";
import { findTypeGroups } from "./shapes.ts";

import type {
  Diagnostic,
  PackageAnalysis,
  PackageRequest,
} from "./contracts.ts";

/**
 * analyzes a package using read-only compiler projects for its applicable configurations
 * @param request eligible package files and selected scope
 * @returns type candidates, error candidates, and explicit diagnostics
 */
export function analyzePackage(request: PackageRequest): PackageAnalysis {
  const configurations = new Map<string | undefined, string[]>();
  for (const file of request.files) {
    const configuration = nearestFile(
      file,
      request.repository_root,
      "tsconfig.json",
    );
    configurations.set(configuration, [
      ...(configurations.get(configuration) ?? []),
      file,
    ]);
  }
  const projects = [...configurations].map(([configuration, files]) => {
    const project = new Project({
      compilerOptions:
        configuration === undefined
          ? {
              noEmit: true,
              strict: true,
              target: ts.ScriptTarget.ESNext,
              module: ts.ModuleKind.Preserve,
              moduleResolution: ts.ModuleResolutionKind.Bundler,
            }
          : readCompilerOptions(configuration, request.files),
    });
    for (const file of request.files) project.addSourceFileAtPath(file);
    project.resolveSourceFileDependencies();
    return { project, files };
  });
  const diagnostics: Diagnostic[] = projects.flatMap(({ project, files }) => {
    const program = project.getProgram().compilerObject;
    return files.flatMap((file) =>
      program
        .getSyntacticDiagnostics(
          project.getSourceFileOrThrow(file).compilerNode,
        )
        .map((diagnostic) => {
          const location = diagnostic.file.getLineAndCharacterOfPosition(
            diagnostic.start,
          );
          return {
            kind: "failure" as const,
            message: ts.flattenDiagnosticMessageText(
              diagnostic.messageText,
              "\n",
            ),
            file,
            line: location.line + 1,
            column: location.character + 1,
          };
        }),
    );
  });
  if (diagnostics.length > 0)
    return {
      reuse_candidates: [],
      extraction_proposals: [],
      error_documentation_candidates: [],
      diagnostics,
    };
  const groups = findTypeGroups(request, projects);
  const selected = new Set(request.selected_files);
  return {
    ...groups,
    diagnostics: [
      ...groups.diagnostics,
      ...projects.flatMap(({ project, files }) => {
        const checker = project.getTypeChecker().compilerObject;
        return files.flatMap((file) => {
          const source = project.getSourceFileOrThrow(file).compilerNode;
          return source.statements.flatMap((statement): Diagnostic[] => {
            const specifier =
              ts.isImportDeclaration(statement) ||
              ts.isExportDeclaration(statement)
                ? statement.moduleSpecifier
                : undefined;
            if (
              specifier === undefined ||
              !ts.isStringLiteral(specifier) ||
              checker.getSymbolAtLocation(specifier) !== undefined
            )
              return [];
            const position = source.getLineAndCharacterOfPosition(
              specifier.getStart(source),
            );
            return [
              {
                kind: "review",
                file,
                line: position.line + 1,
                column: position.character + 1,
                message: `unresolved module ${specifier.text}; dependency evidence requires review`,
              },
            ];
          });
        });
      }),
    ],
    error_documentation_candidates: projects.flatMap(({ project, files }) =>
      files
        .filter((file) => selected.has(file))
        .flatMap((file) =>
          findErrorDocumentation(
            project.getSourceFileOrThrow(file),
            project.getTypeChecker().compilerObject,
          ),
        ),
    ),
  };
}

function readCompilerOptions(
  configuration: string,
  files: readonly string[],
): ts.CompilerOptions {
  const source = ts.readConfigFile(configuration, ts.sys.readFile);
  if (source.error !== undefined)
    throw new Error(
      ts.flattenDiagnosticMessageText(source.error.messageText, "\n"),
    );
  const data: Record<string, unknown> = source.config;
  // package discovery owns file eligibility; config contributes settings and extends
  const parsed = ts.parseJsonConfigFileContent(
    { ...data, files: [...files], include: [] },
    ts.sys,
    dirname(configuration),
    { noEmit: true },
    configuration,
  );
  if (parsed.errors.length > 0)
    throw new Error(
      parsed.errors
        .map((error) =>
          ts.flattenDiagnosticMessageText(error.messageText, "\n"),
        )
        .join("\n"),
    );
  return parsed.options;
}

if (import.meta.main) {
  try {
    const request = JSON.parse(await Bun.stdin.text()) as PackageRequest;
    process.stdout.write(`${JSON.stringify(analyzePackage(request))}\n`);
  } catch (error) {
    process.stderr.write(`${(error as Error).message}\n`);
    process.exitCode = 1;
  }
}

import { ts } from "ts-morph@28";

import type { Project } from "ts-morph@28";

import type {
  Diagnostic,
  Location,
  Occurrence,
  PackageAnalysis,
  PackageRequest,
  SharedContract,
  TypeGroup,
} from "./contracts.ts";

interface ProjectFiles {
  readonly project: Project;
  readonly files: readonly string[];
}

interface Shape {
  readonly kind: string;
  readonly value?: string;
  readonly children: readonly Shape[];
  readonly node: ts.Node;
  readonly parameter?: ts.TypeParameterDeclaration;
  readonly unresolved: boolean;
}

interface TypeOccurrence {
  readonly shape: Shape;
  readonly location: Occurrence;
  readonly checker: ts.TypeChecker;
}

interface NamedShape {
  readonly name: string;
  readonly shape: Shape;
  readonly declaration: ts.TypeAliasDeclaration | ts.InterfaceDeclaration;
  readonly checker: ts.TypeChecker;
}

interface ShapeContext {
  readonly checker: ts.TypeChecker;
  readonly localBindings: ReadonlyMap<ts.Symbol, string>;
  readonly parameters: ReadonlySet<ts.Symbol>;
}

type ShapeKey = readonly [string, string | undefined, readonly ShapeKey[]];

/**
 * groups structurally identical anonymous types and matches named generic contracts
 * @param request package identity and selected scope
 * @param projects read-only compiler contexts and their owning files
 * @returns deterministic advisory groups and unresolved-reference diagnostics
 */
export function findTypeGroups(
  request: PackageRequest,
  projects: readonly ProjectFiles[],
): Pick<
  PackageAnalysis,
  "reuse_candidates" | "extraction_proposals" | "diagnostics"
> {
  const selected = new Set(request.selected_files);
  const occurrences: TypeOccurrence[] = [];
  const named: NamedShape[] = [];
  for (const { project, files } of projects) {
    const checker = project.getTypeChecker().compilerObject;
    for (const file of files) {
      const source = project.getSourceFileOrThrow(file).compilerNode;
      const visit = (node: ts.Node): void => {
        if (
          ts.isTypeAliasDeclaration(node) ||
          ts.isInterfaceDeclaration(node)
        ) {
          const declarations = ts.isInterfaceDeclaration(node)
            ? (checker
                .getSymbolAtLocation(node.name)
                ?.declarations?.filter(ts.isInterfaceDeclaration) ?? [node])
            : [node];
          const target = ts.isTypeAliasDeclaration(node) ? node.type : node;
          const parameters = new Set(
            (node.typeParameters ?? []).flatMap((parameter) => {
              const symbol = checker.getSymbolAtLocation(parameter.name);
              return symbol === undefined ? [] : [symbol];
            }),
          );
          if (
            declarations[0] === node &&
            !declarations.some(
              (declaration) =>
                ts.isInterfaceDeclaration(declaration) &&
                declaration.heritageClauses !== undefined,
            )
          )
            named.push({
              name: node.name.text,
              declaration: node,
              checker,
              shape: makeShape(target, {
                checker,
                parameters,
                localBindings: localBindings(target, checker),
              }),
            });
        }
        if (
          (ts.isTypeLiteralNode(node) || ts.isFunctionTypeNode(node)) &&
          !(ts.isTypeAliasDeclaration(node.parent) && node.parent.type === node)
        ) {
          occurrences.push({
            checker,
            shape: makeShape(node, {
              checker,
              parameters: new Set(),
              localBindings: localBindings(node, checker),
            }),
            location: {
              ...location(node),
              selected: selected.has(file),
              text: node.getText(source),
            },
          });
        }
        ts.forEachChild(node, visit);
      };
      visit(source);
    }
  }
  const grouped = new Map<string, TypeOccurrence[]>();
  const diagnostics: (Diagnostic & Location)[] = [];
  for (const occurrence of occurrences) {
    if (occurrence.shape.unresolved) {
      diagnostics.push({
        kind: "review",
        ...location(occurrence.shape.node),
        message:
          "unresolved type reference; shared-contract identity requires review",
      });
      continue;
    }
    const key = shapeKey(occurrence.shape);
    grouped.set(key, [...(grouped.get(key) ?? []), occurrence]);
  }
  const reuse: TypeGroup[] = [];
  const extraction: TypeGroup[] = [];
  for (const group of grouped.values()) {
    if (!group.some((occurrence) => occurrence.location.selected)) continue;
    const first = group[0]!;
    const candidates = named.flatMap((candidate) =>
      matchContract(candidate, first),
    );
    const result: TypeGroup = {
      rule_id: "TYP-TYPE-09",
      package_root: request.root,
      occurrences: group
        .map((occurrence) => occurrence.location)
        .sort(compareLocation),
      candidates: candidates.sort(compareLocation),
    };
    if (candidates.length > 0) reuse.push(result);
    else if (group.length >= 2 && first.shape.kind === "object")
      extraction.push(result);
  }
  const compareGroup = (first: TypeGroup, second: TypeGroup): number =>
    compareLocation(first.occurrences[0]!, second.occurrences[0]!);
  return {
    reuse_candidates: reuse.sort(compareGroup),
    extraction_proposals: extraction.sort(compareGroup),
    diagnostics: diagnostics.sort(
      (first, second) =>
        first.file.localeCompare(second.file) || first.line - second.line,
    ),
  };
}

function matchContract(
  candidate: NamedShape,
  occurrence: TypeOccurrence,
): SharedContract[] {
  if (candidate.shape.unresolved) return [];
  const bindings = new Map<ts.TypeParameterDeclaration, Shape>();
  if (!matches(candidate.shape, occurrence.shape, bindings)) return [];
  const arguments_: string[] = [];
  for (const parameter of candidate.declaration.typeParameters ?? []) {
    const inferred = bindings.get(parameter);
    if (inferred === undefined) {
      if (parameter.default === undefined) return [];
      arguments_.push(parameter.default.getText());
    } else {
      if (parameter.constraint !== undefined) {
        const actualType = occurrence.checker.getTypeAtLocation(inferred.node);
        const constraintType = candidate.checker.getTypeAtLocation(
          parameter.constraint,
        );
        if (
          candidate.checker !== occurrence.checker ||
          !candidate.checker.isTypeAssignableTo(actualType, constraintType)
        )
          return [];
      }
      arguments_.push(inferred.node.getText());
    }
  }
  return [
    {
      ...location(candidate.declaration),
      name: candidate.name,
      type_arguments: arguments_,
    },
  ];
}

function matches(
  pattern: Shape,
  actual: Shape,
  bindings: Map<ts.TypeParameterDeclaration, Shape>,
): boolean {
  if (pattern.parameter !== undefined) {
    const previous = bindings.get(pattern.parameter);
    if (previous !== undefined) return shapeKey(previous) === shapeKey(actual);
    bindings.set(pattern.parameter, actual);
    return true;
  }
  return (
    pattern.kind === actual.kind &&
    pattern.value === actual.value &&
    pattern.children.length === actual.children.length &&
    pattern.children.every((child, index) =>
      matches(child, actual.children[index]!, bindings),
    )
  );
}

function makeShape(node: ts.Node, context: ShapeContext): Shape {
  if (ts.isParenthesizedTypeNode(node)) return makeShape(node.type, context);
  if (
    ts.isComputedPropertyName(node) &&
    !ts.isStringLiteralLike(node.expression) &&
    !ts.isNumericLiteral(node.expression)
  ) {
    const symbol = resolvedSymbol(node.expression, context.checker);
    const identity = symbol === undefined ? undefined : symbolIdentity(symbol);
    return {
      node,
      kind: "computed",
      value: identity,
      children: [],
      unresolved: identity === undefined,
    };
  }
  if (ts.isTypeReferenceNode(node) || ts.isTypeQueryNode(node)) {
    const name = ts.isTypeReferenceNode(node) ? node.typeName : node.exprName;
    const symbol = resolvedSymbol(name, context.checker);
    const parameter =
      symbol !== undefined && context.parameters.has(symbol)
        ? symbol.declarations?.find(ts.isTypeParameterDeclaration)
        : undefined;
    if (
      parameter !== undefined &&
      ts.isTypeReferenceNode(node) &&
      node.typeArguments === undefined
    )
      return {
        node,
        kind: "parameter",
        children: [],
        parameter,
        unresolved: false,
      };
    const children = (node.typeArguments ?? []).map((child) =>
      makeShape(child, context),
    );
    const identity =
      symbol === undefined
        ? undefined
        : (context.localBindings.get(symbol) ?? symbolIdentity(symbol));
    return {
      node,
      kind: ts.isTypeReferenceNode(node) ? "reference" : "query",
      value: identity,
      children,
      unresolved:
        identity === undefined || children.some((child) => child.unresolved),
    };
  }
  const nodes: ts.Node[] = [];
  if (ts.isInterfaceDeclaration(node)) {
    const declarations = context.checker
      .getSymbolAtLocation(node.name)
      ?.declarations?.filter(ts.isInterfaceDeclaration) ?? [node];
    nodes.push(
      ...declarations.flatMap((declaration) => [...declaration.members]),
    );
  } else if (ts.isTypeLiteralNode(node)) nodes.push(...node.members);
  else
    ts.forEachChild(node, (child) => {
      nodes.push(child);
    });
  const children = nodes
    .filter(
      (child) =>
        !(ts.isParameter(node) && child === node.name) &&
        !(ts.isTypeParameterDeclaration(node) && child === node.name),
    )
    .map((child) => makeShape(child, context));
  const kind =
    ts.isInterfaceDeclaration(node) || ts.isTypeLiteralNode(node)
      ? "object"
      : ts.SyntaxKind[node.kind];
  const value =
    ts.isIdentifier(node) ||
    ts.isStringLiteralLike(node) ||
    ts.isNumericLiteral(node)
      ? node.text
      : undefined;
  return {
    node,
    kind,
    value,
    children,
    unresolved: children.some((child) => child.unresolved),
  };
}

function localBindings(
  root: ts.Node,
  checker: ts.TypeChecker,
): ReadonlyMap<ts.Symbol, string> {
  const bindings = new Map<ts.Symbol, string>();
  const visit = (node: ts.Node): void => {
    if (ts.isTypeParameterDeclaration(node)) {
      const symbol = checker.getSymbolAtLocation(node.name);
      if (symbol !== undefined) bindings.set(symbol, `local:${bindings.size}`);
    }
    ts.forEachChild(node, visit);
  };
  visit(root);
  return bindings;
}

function resolvedSymbol(
  node: ts.Node,
  checker: ts.TypeChecker,
): ts.Symbol | undefined {
  const symbol = checker.getSymbolAtLocation(node);
  if (symbol === undefined) return undefined;
  const resolved =
    (symbol.flags & ts.SymbolFlags.Alias) === 0
      ? symbol
      : checker.getAliasedSymbol(symbol);
  return resolved.declarations === undefined ? undefined : resolved;
}

function symbolIdentity(symbol: ts.Symbol): string | undefined {
  return symbol.declarations
    ?.map(
      (declaration) =>
        `${declaration.getSourceFile().fileName}:${declaration.pos}:${declaration.end}`,
    )
    .sort()
    .join("|");
}

function shapeKey(shape: Shape): string {
  return JSON.stringify(shapeData(shape));
}

function shapeData(shape: Shape): ShapeKey {
  return [shape.kind, shape.value, shape.children.map(shapeData)];
}

function location(node: ts.Node): Location {
  const source = node.getSourceFile();
  const position = source.getLineAndCharacterOfPosition(node.getStart(source));
  return {
    file: source.fileName,
    line: position.line + 1,
    column: position.character + 1,
  };
}

function compareLocation(first: Location, second: Location): number {
  return (
    first.file.localeCompare(second.file) ||
    first.line - second.line ||
    first.column - second.column
  );
}

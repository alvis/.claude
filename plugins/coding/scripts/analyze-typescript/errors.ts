import { ts } from "ts-morph@28";

import type { SourceFile } from "ts-morph@28";

import type { ErrorCandidate, Location } from "./contracts.ts";

interface ErrorEvidence {
  readonly identities: ReadonlySet<string>;
  readonly unresolved: boolean;
  readonly raised: boolean;
}

interface EvidenceContext {
  readonly checker: ts.TypeChecker;
  readonly owner: ts.FunctionLikeDeclaration;
}

const emptyEvidence: ErrorEvidence = {
  identities: new Set(),
  unresolved: false,
  raised: false,
};

/**
 * checks each documented error against escaping local throw and rejection evidence
 * @param source selected eligible source file
 * @param checker read-only compiler checker
 * @returns unsupported and uncertain claims requiring semantic review
 */
export function findErrorDocumentation(
  source: SourceFile,
  checker: ts.TypeChecker,
): ErrorCandidate[] {
  const candidates: ErrorCandidate[] = [];
  const visit = (node: ts.Node): void => {
    if (isFunction(node)) {
      const tags = ts
        .getJSDocTags(node)
        .filter((tag) =>
          ["throws", "exception", "rejects"].includes(tag.tagName.text),
        );
      if (tags.length > 0) {
        const context = { checker, owner: node };
        const evidence =
          node.body === undefined
            ? { ...emptyEvidence, unresolved: true }
            : ts.isBlock(node.body)
              ? inspectBody(node.body, context, false)
              : inspectPromise(node.body, context, new Set());
        for (const tag of tags) {
          const text = tag.getText(source.compilerNode).replace(/^@\w+\s*/, "");
          const documented =
            /^\{([^}]+)\}/.exec(text)?.[1]?.trim() ??
            /^([\w$.]*(?:Error|Exception))\b/.exec(text)?.[1] ??
            "unspecified";
          const names = documented.split("|").map((name) => name.trim());
          const supported =
            documented === "unspecified"
              ? evidence.raised && !evidence.unresolved
              : names.every((name) => evidence.identities.has(name));
          if (!supported)
            candidates.push({
              rule_id: "DOC-CONT-06",
              ...location(tag),
              function_name: functionName(node),
              documented_error: documented,
              reason: evidence.unresolved ? "unresolved" : "unsupported",
              message: evidence.unresolved
                ? "local error identity or control flow requires review"
                : "no escaping local throw or rejection supports this documented error",
            });
        }
      }
    }
    ts.forEachChild(node, visit);
  };
  visit(source.compilerNode);
  return candidates;
}

function inspectBody(
  node: ts.Node,
  context: EvidenceContext,
  caught: boolean,
): ErrorEvidence {
  if (isFunction(node)) return emptyEvidence;
  if (ts.isThrowStatement(node))
    return caught
      ? emptyEvidence
      : errorIdentity(node.expression, context.checker);
  if (ts.isTryStatement(node)) {
    const body = inspectBody(
      node.tryBlock,
      context,
      caught || node.catchClause !== undefined,
    );
    const handler =
      node.catchClause === undefined
        ? emptyEvidence
        : inspectBody(node.catchClause.block, context, caught);
    const finalizer =
      node.finallyBlock === undefined
        ? emptyEvidence
        : inspectBody(node.finallyBlock, context, caught);
    if (node.finallyBlock !== undefined && hasReturn(node.finallyBlock))
      return mergeEvidence([finalizer, { ...emptyEvidence, unresolved: true }]);
    return mergeEvidence([body, handler, finalizer]);
  }
  if (ts.isReturnStatement(node) && node.expression !== undefined) {
    const expression = unwrap(node.expression);
    if (caught && ts.isAwaitExpression(expression)) return emptyEvidence;
    return inspectPromise(expression, context, new Set());
  }
  if (ts.isAwaitExpression(node))
    return caught
      ? emptyEvidence
      : inspectPromise(node.expression, context, new Set());
  const children: ErrorEvidence[] = [];
  ts.forEachChild(node, (child) => {
    children.push(inspectBody(child, context, caught));
  });
  return mergeEvidence(children);
}

function inspectPromise(
  input: ts.Expression,
  context: EvidenceContext,
  seen: ReadonlySet<ts.Symbol>,
): ErrorEvidence {
  const expression = unwrap(input);
  if (ts.isAwaitExpression(expression))
    return inspectPromise(expression.expression, context, seen);
  if (ts.isConditionalExpression(expression))
    return mergeEvidence([
      inspectPromise(expression.whenTrue, context, seen),
      inspectPromise(expression.whenFalse, context, seen),
    ]);
  if (ts.isIdentifier(expression)) {
    const symbol = context.checker.getSymbolAtLocation(expression);
    if (symbol === undefined || seen.has(symbol)) return emptyEvidence;
    const declaration = symbol.valueDeclaration;
    if (
      declaration !== undefined &&
      ts.isVariableDeclaration(declaration) &&
      ownsDeclaration(declaration, context.owner) &&
      declaration.initializer !== undefined &&
      ts.isVariableDeclarationList(declaration.parent) &&
      (declaration.parent.flags & ts.NodeFlags.Const) !== 0
    )
      return inspectPromise(
        declaration.initializer,
        context,
        new Set([...seen, symbol]),
      );
    return emptyEvidence;
  }
  if (
    ts.isCallExpression(expression) &&
    ts.isPropertyAccessExpression(expression.expression)
  ) {
    const access = expression.expression;
    if (
      access.name.text === "reject" &&
      isPromise(access.expression, context.checker)
    )
      return expression.arguments[0] === undefined
        ? { ...emptyEvidence, raised: true, unresolved: true }
        : errorIdentity(expression.arguments[0], context.checker);
    if (
      (access.name.text === "catch" &&
        !isAbsentHandler(expression.arguments[0], context.checker)) ||
      (access.name.text === "then" &&
        !isAbsentHandler(expression.arguments[1], context.checker))
    )
      return emptyEvidence;
    if (
      access.name.text === "then" ||
      access.name.text === "finally" ||
      access.name.text === "catch"
    )
      return inspectPromise(access.expression, context, seen);
  }
  if (
    ts.isNewExpression(expression) &&
    isPromise(expression.expression, context.checker)
  ) {
    const executor = expression.arguments?.[0];
    if (
      executor === undefined ||
      (!ts.isArrowFunction(executor) && !ts.isFunctionExpression(executor))
    )
      return { ...emptyEvidence, unresolved: true };
    const reject = executor.parameters[1];
    const rejectSymbol =
      reject === undefined
        ? undefined
        : context.checker.getSymbolAtLocation(reject.name);
    const inspectExecutor = (node: ts.Node, caught: boolean): ErrorEvidence => {
      if (isFunction(node)) return emptyEvidence;
      if (ts.isThrowStatement(node))
        return caught
          ? emptyEvidence
          : errorIdentity(node.expression, context.checker);
      if (
        ts.isCallExpression(node) &&
        ts.isIdentifier(node.expression) &&
        rejectSymbol !== undefined &&
        context.checker.getSymbolAtLocation(node.expression) === rejectSymbol
      )
        return node.arguments[0] === undefined
          ? { ...emptyEvidence, raised: true, unresolved: true }
          : errorIdentity(node.arguments[0], context.checker);
      if (ts.isTryStatement(node))
        return mergeEvidence([
          inspectExecutor(
            node.tryBlock,
            caught || node.catchClause !== undefined,
          ),
          ...(node.catchClause === undefined
            ? []
            : [inspectExecutor(node.catchClause.block, caught)]),
          ...(node.finallyBlock === undefined
            ? []
            : [inspectExecutor(node.finallyBlock, caught)]),
        ]);
      const children: ErrorEvidence[] = [];
      ts.forEachChild(node, (child) => {
        children.push(inspectExecutor(child, caught));
      });
      return mergeEvidence(children);
    };
    return inspectExecutor(executor.body, false);
  }
  return emptyEvidence;
}

function errorIdentity(
  expression: ts.Expression,
  checker: ts.TypeChecker,
): ErrorEvidence {
  const type = checker.getTypeAtLocation(expression);
  const types = type.isUnion() ? type.types : [type];
  const identities = types.flatMap((member) => {
    const symbol = member.getSymbol();
    return symbol === undefined || symbol.declarations === undefined
      ? []
      : [symbol.name];
  });
  if (ts.isNewExpression(expression)) {
    const symbol = checker.getSymbolAtLocation(expression.expression);
    const target =
      symbol !== undefined && (symbol.flags & ts.SymbolFlags.Alias) !== 0
        ? checker.getAliasedSymbol(symbol)
        : symbol;
    if (target?.declarations !== undefined)
      identities.push(target.name, expression.expression.getText());
  }
  return {
    identities: new Set(identities),
    unresolved:
      identities.length === 0 ||
      types.some(
        (member) =>
          (member.flags &
            (ts.TypeFlags.Any |
              ts.TypeFlags.Unknown |
              ts.TypeFlags.TypeParameter)) !==
          0,
      ),
    raised: true,
  };
}

function isPromise(
  expression: ts.Expression,
  checker: ts.TypeChecker,
): boolean {
  if (!ts.isIdentifier(expression) || expression.text !== "Promise")
    return false;
  const symbol = checker.getSymbolAtLocation(expression);
  return (
    symbol?.declarations?.some((declaration) =>
      /(?:^|[/\\])lib\.[^/\\]+\.d\.ts$/.test(
        declaration.getSourceFile().fileName,
      ),
    ) ?? false
  );
}

function isAbsentHandler(
  expression: ts.Expression | undefined,
  checker: ts.TypeChecker,
): boolean {
  if (expression === undefined) return true;
  const type = checker.getTypeAtLocation(expression);
  const members = type.isUnion() ? type.types : [type];
  return members.every(
    (member) =>
      (member.flags & (ts.TypeFlags.Undefined | ts.TypeFlags.Null)) !== 0,
  );
}

function ownsDeclaration(
  node: ts.Node,
  owner: ts.FunctionLikeDeclaration,
): boolean {
  let ancestor = node.parent;
  while (ancestor !== undefined) {
    if (isFunction(ancestor)) return ancestor === owner;
    ancestor = ancestor.parent;
  }
  return false;
}

function unwrap(expression: ts.Expression): ts.Expression {
  if (
    ts.isParenthesizedExpression(expression) ||
    ts.isAsExpression(expression) ||
    ts.isTypeAssertionExpression(expression) ||
    ts.isNonNullExpression(expression) ||
    ts.isSatisfiesExpression(expression)
  )
    return unwrap(expression.expression);
  return expression;
}

function isFunction(node: ts.Node): node is ts.FunctionLikeDeclaration {
  return (
    ts.isFunctionDeclaration(node) ||
    ts.isFunctionExpression(node) ||
    ts.isArrowFunction(node) ||
    ts.isMethodDeclaration(node) ||
    ts.isConstructorDeclaration(node) ||
    ts.isGetAccessorDeclaration(node) ||
    ts.isSetAccessorDeclaration(node)
  );
}

function hasReturn(node: ts.Node): boolean {
  if (isFunction(node)) return false;
  return (
    ts.isReturnStatement(node) || (ts.forEachChild(node, hasReturn) ?? false)
  );
}

function mergeEvidence(evidence: readonly ErrorEvidence[]): ErrorEvidence {
  return {
    identities: new Set(evidence.flatMap((item) => [...item.identities])),
    unresolved: evidence.some((item) => item.unresolved),
    raised: evidence.some((item) => item.raised),
  };
}

function functionName(node: ts.FunctionLikeDeclaration): string {
  if (node.name !== undefined) return node.name.getText();
  if (
    ts.isVariableDeclaration(node.parent) ||
    ts.isPropertyAssignment(node.parent)
  )
    return node.parent.name.getText();
  return ts.isConstructorDeclaration(node) ? "constructor" : "anonymous";
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

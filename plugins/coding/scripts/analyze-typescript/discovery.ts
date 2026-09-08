import { spawnSync } from "node:child_process";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, isAbsolute, relative, resolve, sep } from "node:path";

import { eligibleFiles } from "../lint_profile_runner.ts";

import type { AnalysisOptions, PackageScope } from "./contracts.ts";

interface IgnoreRule {
  readonly root: string;
  readonly pattern: string;
  readonly negate: boolean;
}

const excludedDirectories = new Set([
  ".git",
  ".jj",
  "node_modules",
  "vendor",
  "generated",
  "__generated__",
  "dist",
  "build",
  "coverage",
]);
const sourceExtension = /\.(?:[cm]?ts|tsx)$/;

/**
 * discovers eligible package peers while preserving selection and package boundaries
 * @param options selected paths and repository boundary
 * @param profile validated lint eligibility profile
 * @returns deterministically ordered package coverage
 * @throws when a selected file is outside the repository or does not exist as a file
 */
export function discoverPackages(
  options: AnalysisOptions,
  profile: unknown,
): PackageScope[] {
  const root = resolve(options.repositoryRoot ?? process.cwd());
  const selected = [
    ...new Set(options.files.map((file) => resolve(root, file))),
  ].sort();
  for (const file of selected) {
    if (!inside(root, file))
      throw new Error(`selected file escapes repository: ${file}`);
    if (!existsSync(file) || !statSync(file).isFile())
      throw new Error(`selected file does not exist: ${file}`);
  }
  const hasGit =
    spawnSync("git", ["-C", root, "rev-parse", "--show-toplevel"], {
      encoding: "utf8",
    }).status === 0;
  const sourceFiles = walk(root, [], hasGit).filter(
    (file) =>
      sourceExtension.test(file) &&
      !/\.(?:generated|gen)\.[^.]+$/.test(file) &&
      !isGenerated(file),
  );
  const lintProfile = profile as Parameters<typeof eligibleFiles>[1];
  const eligible = sourceFiles.filter(
    (file) =>
      eligibleFiles([file], lintProfile).length > 0 &&
      eligibleFiles([relative(root, file).split(sep).join("/")], lintProfile)
        .length > 0,
  );
  const eligibleSet = new Set(eligible);
  const byPackage = new Map<string, string[]>();
  for (const file of selected.filter((file) => eligibleSet.has(file))) {
    const owner = packageRoot(file, root);
    const paths = byPackage.get(owner) ?? [];
    paths.push(file);
    byPackage.set(owner, paths);
  }
  return [...byPackage]
    .sort(([first], [second]) => first.localeCompare(second))
    .map(([owner, files]) => ({
      root: owner,
      files: eligible.filter((file) => packageRoot(file, root) === owner),
      selected_files: files,
    }));
}

/**
 * finds the closest named configuration without crossing the repository boundary
 * @param file source path
 * @param root repository boundary
 * @param name configuration basename
 * @returns existing configuration path, if any
 */
export function nearestFile(
  file: string,
  root: string,
  name: string,
): string | undefined {
  let directory = dirname(file);
  while (inside(root, directory)) {
    const candidate = resolve(directory, name);
    if (existsSync(candidate)) return candidate;
    if (directory === root) break;
    directory = dirname(directory);
  }
  return undefined;
}

function packageRoot(file: string, root: string): string {
  const manifest = nearestFile(file, root, "package.json");
  return manifest === undefined ? root : dirname(manifest);
}

function inside(root: string, file: string): boolean {
  const path = relative(root, file);
  return (
    path === "" ||
    (path !== ".." && !path.startsWith(`..${sep}`) && !isAbsolute(path))
  );
}

function walk(
  directory: string,
  inherited: readonly IgnoreRule[],
  hasGit: boolean,
): string[] {
  const ignoreFile = resolve(directory, ".gitignore");
  const rules = [
    ...inherited,
    ...(!hasGit && existsSync(ignoreFile)
      ? readFileSync(ignoreFile, "utf8")
          .split(/\r?\n/)
          .filter((line) => line !== "" && !line.startsWith("#"))
          .map((line) => ({
            root: directory,
            pattern: line.replace(/^!/, "").replace(/\/$/, ""),
            negate: line.startsWith("!"),
          }))
      : []),
  ];
  const entries = readdirSync(directory, { withFileTypes: true })
    .filter(
      (entry) =>
        !entry.isSymbolicLink() && !excludedDirectories.has(entry.name),
    )
    .sort((first, second) => first.name.localeCompare(second.name));
  const ignored = hasGit
    ? gitIgnored(
        directory,
        entries.map((entry) => resolve(directory, entry.name)),
      )
    : new Set<string>();
  return entries.flatMap((entry) => {
    const file = resolve(directory, entry.name);
    if (ignored.has(file) || isIgnored(file, rules)) return [];
    if (entry.isDirectory()) return walk(file, rules, hasGit);
    return entry.isFile() ? [file] : [];
  });
}

function isIgnored(file: string, rules: readonly IgnoreRule[]): boolean {
  let ignored = false;
  for (const rule of rules) {
    const path = relative(rule.root, file).split(sep).join("/");
    const pattern = rule.pattern.replace(/^\//, "");
    const candidates = rule.pattern.includes("/") ? [path] : path.split("/");
    if (candidates.some((part) => new Bun.Glob(pattern).match(part)))
      ignored = !rule.negate;
  }
  return ignored;
}

function gitIgnored(
  root: string,
  files: readonly string[],
): ReadonlySet<string> {
  if (files.length === 0) return new Set();
  const result = spawnSync(
    "git",
    ["-C", root, "check-ignore", "--no-index", "-z", "--stdin"],
    { input: files.join("\0") + "\0", encoding: "utf8", maxBuffer: Infinity },
  );
  if (result.status !== 0 && result.status !== 1)
    throw new Error(
      `unable to resolve Git exclusions: ${result.stderr || result.error?.message}`,
    );
  return new Set(result.stdout.split("\0").filter(Boolean));
}

function isGenerated(file: string): boolean {
  const header = /^\s*(?:(?:\/\/[^\n]*(?:\n|$)|\/\*[\s\S]*?\*\/)\s*)*/.exec(
    readFileSync(file, "utf8"),
  )![0];
  return /@generated\b|auto[- ]generated|automatically generated/i.test(header);
}

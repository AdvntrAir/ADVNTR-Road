import { readFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import YAML from 'yaml';

/**
 * Reads intel/intel-place-registry.yaml (repo root, outside apps/web) so tag
 * hubs can link to the guide a place already has. This file is the single
 * source of truth per the pipeline's registry doc and is never duplicated
 * into the site — read directly, not copied.
 *
 * Resolved by walking up from process.cwd() rather than import.meta.url:
 * Vite bundles this module into dist/.prerender/ at build time, which
 * rewrites import.meta.url to the output location, not the source one.
 */
export interface RegistryPlace {
  slug: string;
  label: string;
  guide_status?: string;
  guide_url?: string;
}

let cache: Map<string, RegistryPlace> | null = null;

function findRegistryPath(): string {
  let dir = process.cwd();
  for (let i = 0; i < 8; i++) {
    const candidate = path.join(dir, 'intel', 'intel-place-registry.yaml');
    if (existsSync(candidate)) return candidate;
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  throw new Error('intel-place-registry.yaml not found walking up from ' + process.cwd());
}

export function getPlaceRegistry(): Map<string, RegistryPlace> {
  if (cache) return cache;

  const raw = readFileSync(findRegistryPath(), 'utf-8');
  const parsed = YAML.parse(raw) as { places: RegistryPlace[] };

  cache = new Map(parsed.places.map((p) => [p.slug, p]));
  return cache;
}

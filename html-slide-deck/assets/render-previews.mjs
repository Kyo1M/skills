#!/usr/bin/env node
/**
 * render-previews.mjs — 見本 HTML（19 型＋ボディ部品）を PNG に書き出す
 *
 * 使い方:
 *   node render-previews.mjs                 # 全件
 *   node render-previews.mjs 01-cover.html   # 1 件だけ（拡張子は省略可）
 *   npm run previews
 *
 * 入力: assets/previews-src/slides/*.html・assets/previews-src/guidelines/*.html
 *       各ファイル先頭の `<!-- @dsCard group="…" viewport="WxH" name="…" -->` の
 *       viewport をそのまま撮影サイズに使う（無ければ 1920×1080）。
 * 出力: references/previews/<元ファイル名>.png（01-cover.png / parts-icons.png …）
 *
 * 見本 HTML は runtime を使わない素の HTML だが、`../../tokens/*.css` を相対参照するため
 * check-slides.mjs と同じ静的サーバ（assets/ をルート）で配信して開く。Google Fonts を
 * 読むのでネットワークが要る。
 */
import { chromium } from 'playwright-core';
import { mkdir, readFile, readdir } from 'node:fs/promises';
import { basename, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { startStaticServer } from './lib/static-server.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const SRC_DIRS = ['previews-src/slides', 'previews-src/guidelines'];
const OUT_DIR = resolve(HERE, '../references/previews');
const DEFAULT_VIEWPORT = { width: 1920, height: 1080 };

const args = process.argv.slice(2).filter((a) => !a.startsWith('-'));
const only = args.length ? new Set(args.map((a) => (a.endsWith('.html') ? a : a + '.html'))) : null;

async function collect() {
  const files = [];
  for (const dir of SRC_DIRS) {
    const abs = resolve(HERE, dir);
    let names;
    try {
      names = await readdir(abs);
    } catch {
      console.error(`スキップ: ${dir} が見つかりません`);
      continue;
    }
    for (const name of names.sort()) {
      if (!name.endsWith('.html')) continue;
      if (only && !only.has(name)) continue;
      files.push({ name, dir, path: resolve(abs, name), url: `/${dir}/${name}` });
    }
  }
  return files;
}

function parseCard(html) {
  const m = html.match(/<!--\s*@dsCard([\s\S]*?)-->/);
  const card = { viewport: { ...DEFAULT_VIEWPORT }, name: '', group: '' };
  if (!m) return card;
  const attrs = m[1];
  const vp = attrs.match(/viewport\s*=\s*"(\d+)\s*[x×]\s*(\d+)"/i);
  if (vp) card.viewport = { width: Number(vp[1]), height: Number(vp[2]) };
  const nm = attrs.match(/name\s*=\s*"([^"]*)"/);
  if (nm) card.name = nm[1];
  const gr = attrs.match(/group\s*=\s*"([^"]*)"/);
  if (gr) card.group = gr[1];
  return card;
}

const files = await collect();
if (!files.length) {
  console.error('実行エラー: 対象の見本 HTML がありません');
  process.exit(2);
}

await mkdir(OUT_DIR, { recursive: true });

const srv = await startStaticServer({ root: HERE });
let browser;
let exitCode = 0;
try {
  browser = await chromium.launch({ channel: 'chrome', headless: true });
  console.log(`render-previews: ${files.length} 件 → ${OUT_DIR}\n`);

  for (const f of files) {
    const html = await readFile(f.path, 'utf8');
    const card = parseCard(html);
    const page = await browser.newPage({ viewport: card.viewport, deviceScaleFactor: 1 });
    try {
      await page.goto(srv.origin + f.url, { waitUntil: 'load', timeout: 20000 });
      try {
        await page.waitForLoadState('networkidle', { timeout: 10000 });
      } catch {
        // Google Fonts が遅くても続行する
      }
      await page.evaluate(() => document.fonts.ready).catch(() => {});
      const out = resolve(OUT_DIR, basename(f.name, '.html') + '.png');
      await page.screenshot({
        path: out,
        clip: { x: 0, y: 0, width: card.viewport.width, height: card.viewport.height },
      });
      console.log(
        `✓ ${basename(out).padEnd(28)} ${String(card.viewport.width)}×${card.viewport.height}  ${card.name}`
      );
    } catch (e) {
      console.error(`✗ ${f.name}: ${e.message}`);
      exitCode = 1;
    } finally {
      await page.close();
    }
  }
} catch (e) {
  console.error('実行エラー:', e && e.stack ? e.stack : e);
  exitCode = 2;
} finally {
  if (browser) await browser.close();
  await srv.close();
}
process.exit(exitCode);

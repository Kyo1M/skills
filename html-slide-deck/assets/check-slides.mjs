#!/usr/bin/env node
/**
 * check-slides.mjs — html-slide-deck v2 の機械チェック（.dc.html / 1920×1080 / section 単位）
 *
 * 使い方:
 *   node check-slides.mjs <deck.dc.html> [--shots <dir>] [--json <path>]
 *   npm run check -- <deck.dc.html>
 *
 * 検査（FAIL = 出し直し / WARN = 目視で判断）:
 *   FAIL 1. はみ出し   … 1920×1080 の外へ出た子孫要素／footer 帯への食い込み（-30px 以内は WARN）
 *   FAIL 2. 内側クリップ … overflow:hidden の要素で scrollHeight > clientHeight
 *   FAIL 3. フォント下限 … 本文 24px・補助 22px（data-role="caption" / footer 配下）・kicker 18px（data-role="kicker"）
 *   FAIL 4. 禁止ダッシュの残存 … `──`(U+2500 の 2 連以上) / `―`(U+2015) / `—`(U+2014)
 *   FAIL 5. data-speaker-notes の残存
 *   WARN 6. 1 枚にアイコン（<use href="#ic-…">）7 個以上
 *   WARN 7. 1 枚に塗りボックス（白・透明・#F6F5F2 以外の地、面積 40,000px² 以上）4 個以上
 *   WARN 8. 絵文字・アイコンフォント
 *
 * 終了コード: 0 = FAIL なし / 1 = FAIL あり / 2 = 実行エラー
 *
 * --- 計測方式: 「オフライン計測」を採用（runtime を動かさない） ---
 * `.dc.html` は本来 `./support.js` → `<x-import from="./deck-stage.js">` の runtime が
 * unpkg の React/Babel を読み込んでサムネイル列＋ステージを描画する。しかしステージは
 * canvas を `transform: scale()` で縮小表示するため、`getBoundingClientRect()` の値が
 * 表示倍率に依存し、1920×1080 の実寸検査に使えない。可視スライドは 1 枚だけで、
 * 残りは `visibility:hidden` に置かれる点も計測を不安定にする。
 * そこで、入力 HTML から <script> だけを取り除いた同一の DOM をブラウザに解析させ、
 * `<section data-label>` を 1 枚ずつ 1920×1080 の検査ボックスへ実寸で流し込んで測る。
 * helmet の Google Fonts / <style> とアイコンスプライトはそのまま同じ文書に残るので
 * 見た目は runtime 表示と同じで、倍率も入らない。deck-stage が slotted section に当てる
 * `position:absolute / inset:0 / width:100% / height:100% / box-sizing:border-box` は
 * 検査ボックス側の CSS で同値を再現している（overflow だけは、はみ出しを測るために
 * visible にし、スクリーンショット時のみ hidden に戻す）。
 * 副次的な利点として、runtime を動かさないので unpkg への通信が要らず、速く安定する
 * （Google Fonts の読み込みにはネットワークが要る）。
 */
import { chromium } from 'playwright-core';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { basename, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { startStaticServer } from './lib/static-server.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));

const LIMITS = {
  W: 1920,
  H: 1080,
  FOOTER_MARGIN: 30, // footer 上端に対する余裕（投影環境のフォント差の見込み）
  FONT_BODY: 24,
  FONT_CAPTION: 22,
  FONT_KICKER: 18,
  ICON_MAX: 6, // 7 個以上で WARN
  FILL_MIN_AREA: 40000,
  FILL_MAX: 3, // 4 個以上で WARN
};

// ---------------------------------------------------------------- CLI

function parseArgs(argv) {
  const out = { file: null, shots: null, json: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--shots') out.shots = argv[++i];
    else if (a === '--json') out.json = argv[++i];
    else if (a === '-h' || a === '--help') out.help = true;
    else if (!out.file) out.file = a;
  }
  return out;
}

const args = parseArgs(process.argv.slice(2));
if (args.help || !args.file) {
  console.error('usage: node check-slides.mjs <deck.dc.html> [--shots <dir>] [--json <path>]');
  process.exit(args.help ? 0 : 2);
}

const filePath = resolve(args.file);
let source;
try {
  source = await readFile(filePath, 'utf8');
} catch (e) {
  console.error('実行エラー: 入力を読めません:', e.message);
  process.exit(2);
}

if (!/<section[^>]*\sdata-label=/.test(source)) {
  console.error('実行エラー: <section data-label="…"> が 1 枚も見つかりません（.dc.html ですか）');
  process.exit(2);
}

// runtime を動かさないため <script> を全部落とす（support.js の読み込みと x-dc ロジック）
const probeHtml = source.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '');

const PROBE_ROUTE = '/__dc-probe__.html';
const PROBE_CSS = `
  html, body { margin:0; padding:0; background:#fff; }
  #dc-probe-host {
    position:absolute; left:0; top:0;
    width:${LIMITS.W}px; height:${LIMITS.H}px;
    overflow:visible; background:#fff;
  }
  /* deck-stage が ::slotted(*) に当てるのと同じ箱を再現する（overflow だけ visible） */
  #dc-probe-host > section {
    position:absolute !important;
    left:0 !important; top:0 !important; right:auto !important; bottom:auto !important;
    width:${LIMITS.W}px !important; height:${LIMITS.H}px !important;
    box-sizing:border-box !important;
    overflow:visible !important;
    opacity:1 !important; visibility:visible !important; pointer-events:auto !important;
    margin:0 !important;
  }
  #dc-probe-host[data-clip] > section { overflow:hidden !important; }
  #dc-sprite-sink { position:absolute; left:0; top:0; width:0; height:0; overflow:hidden; }
`;

// ---------------------------------------------------------------- in-page

/** 文書を組み替え、section を detach して window.__dc に貯める */
function setupProbe() {
  const head = document.head;
  // helmet の <link>/<style> を head へ移す（body 内でも効くが、head の方が確実）
  document.querySelectorAll('helmet').forEach((h) => {
    Array.from(h.children).forEach((n) => {
      if (/^(LINK|STYLE|META|TITLE)$/.test(n.tagName)) head.appendChild(n);
    });
  });

  const sections = Array.from(document.querySelectorAll('section[data-label]'));

  // アイコンスプライト等、section の外にある <svg> を退避（display:none にすると
  // <use> が解決できないブラウザがあるので、0×0 の overflow:hidden に入れる）
  const sink = document.createElement('div');
  sink.id = 'dc-sprite-sink';
  sink.setAttribute('aria-hidden', 'true');
  document.querySelectorAll('svg').forEach((svg) => {
    if (!svg.closest('section[data-label]') && !svg.closest('#dc-sprite-sink')) sink.appendChild(svg);
  });

  const host = document.createElement('div');
  host.id = 'dc-probe-host';

  sections.forEach((s) => s.remove());
  document.body.replaceChildren(sink, host);

  window.__dc = { sections, host };
  return sections.map((s, i) => ({
    index: i,
    label: s.getAttribute('data-label') || `slide-${i + 1}`,
    screenLabel: s.getAttribute('data-screen-label') || '',
    skip: s.hasAttribute('data-deck-skip'),
  }));
}

function mountSection(i) {
  const { sections, host } = window.__dc;
  host.replaceChildren(sections[i]);
  void host.offsetHeight; // 強制リフロー
  return true;
}

/** 検査ボックスに載っている 1 枚を測る */
function measureMounted(L) {
  const host = document.getElementById('dc-probe-host');
  const sec = host.firstElementChild;
  const EPS = 0.5;
  const hr = host.getBoundingClientRect();
  const ox = hr.left;
  const oy = hr.top;
  const rectOf = (el) => {
    const r = el.getBoundingClientRect();
    return { left: r.left - ox, top: r.top - oy, right: r.right - ox, bottom: r.bottom - oy, width: r.width, height: r.height };
  };
  const attr = (el, n) => (el.getAttribute ? el.getAttribute(n) : null);
  const describe = (el) => {
    const tag = el.tagName.toLowerCase();
    const id = el.id ? '#' + el.id : '';
    const cls = attr(el, 'class') ? '.' + attr(el, 'class').trim().split(/\s+/).join('.') : '';
    const role = attr(el, 'data-role') ? `[data-role=${attr(el, 'data-role')}]` : '';
    const text = (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 44);
    return `<${tag}${id}${cls}${role}>` + (text ? ` "${text}"` : '');
  };
  const directText = (el) =>
    Array.from(el.childNodes)
      .filter((n) => n.nodeType === 3)
      .map((n) => n.textContent)
      .join('')
      .trim();
  const isSvgText = (el) => {
    const t = el.tagName.toLowerCase();
    return t === 'text' || t === 'tspan';
  };
  const textOf = (el) => (isSvgText(el) ? (el.textContent || '').trim() : directText(el));
  const NEUTRAL_BG = new Set(['rgba(0, 0, 0, 0)', 'transparent', 'rgb(255, 255, 255)', 'rgb(246, 245, 242)']);

  const all = Array.from(sec.querySelectorAll('*'));
  const cs = new Map();
  const style = (el) => {
    let s = cs.get(el);
    if (!s) { s = getComputedStyle(el); cs.set(el, s); }
    return s;
  };
  const visible = (el) => {
    const s = style(el);
    return s.display !== 'none' && s.visibility !== 'hidden';
  };

  // footer 帯（[data-footer-title] / [data-page] を含む最も近い absolute 祖先）
  let footerEl = null;
  const mark = sec.querySelector('[data-footer-title], [data-page]');
  if (mark) {
    let e = mark;
    while (e && e !== sec) {
      if (style(e).position === 'absolute') { footerEl = e; break; }
      e = e.parentElement;
    }
    if (!footerEl) footerEl = mark.parentElement || mark;
  }

  // data-role は祖先から継承する（最も近い祖先の指定が効く）
  const ROLE_LABEL = { kicker: 'kicker', caption: 'キャプション', badge: 'バッジ' };
  const roleOf = (el) => {
    let e = el;
    while (e && e !== sec.parentNode) {
      const r = attr(e, 'data-role');
      if (r === 'kicker' || r === 'caption' || r === 'badge') return r;
      e = e.parentElement;
    }
    if (footerEl && footerEl.contains(el)) return 'caption';
    return null;
  };

  // 祖先・子孫が同じ理由で二重に出るのを畳む（内側＝原因の方を残す）
  const innermost = (list, key) =>
    list.filter((o) => !list.some((p) => p !== o && o.el.contains(p.el) && key(p) >= key(o) - 1));

  // ---- 1a. はみ出し
  const outRaw = [];
  for (const el of all) {
    if (!visible(el)) continue;
    const r = rectOf(el);
    if (r.width <= 0 && r.height <= 0) continue;
    const dRight = r.right - L.W;
    const dBottom = r.bottom - L.H;
    if (dRight > EPS || dBottom > EPS) outRaw.push({ el, r, dRight, dBottom });
  }
  const outKept = innermost(outRaw, (o) => Math.max(o.dRight, o.dBottom));
  const outElems = new Set(outKept.map((o) => o.el));
  const overflowOut = outKept.map((o) => {
    const parts = [];
    if (o.dRight > EPS) parts.push(`右端 ${o.r.right.toFixed(0)}px (+${o.dRight.toFixed(0)})`);
    if (o.dBottom > EPS) parts.push(`下端 ${o.r.bottom.toFixed(0)}px (+${o.dBottom.toFixed(0)})`);
    return `${parts.join(' / ')} ${describe(o.el)}`;
  });

  // ---- 1b. footer への食い込み
  const footRaw = [];
  let footerTop = null;
  if (footerEl) {
    const fr = rectOf(footerEl);
    footerTop = fr.top;
    for (const el of all) {
      if (el === footerEl || footerEl.contains(el) || el.contains(footerEl)) continue;
      if (outElems.has(el)) continue; // はみ出しとして既に出している
      if (!visible(el)) continue;
      const s = style(el);
      const hasText = textOf(el) !== '';
      const hasBg = !NEUTRAL_BG.has(s.backgroundColor);
      if (!hasText && !hasBg) continue;
      const r = rectOf(el);
      if (r.width <= 0 || r.height <= 0) continue;
      if (r.right <= fr.left + EPS || r.left >= fr.right - EPS) continue; // 横に重ならない
      if (r.bottom <= footerTop - L.FOOTER_MARGIN) continue;
      footRaw.push({ el, r, over: r.bottom - footerTop, level: r.bottom > footerTop + EPS ? 'FAIL' : 'WARN' });
    }
  }
  const footerHits = innermost(footRaw, (o) => o.over)
    .sort((a, b) => b.over - a.over)
    .map((o) => ({
      level: o.level,
      msg:
        o.level === 'FAIL'
          ? `footer に重なり: 下端 ${o.r.bottom.toFixed(0)}px > footer 上端 ${footerTop.toFixed(0)}px ${describe(o.el)}`
          : `footer への余裕不足: 下端 ${o.r.bottom.toFixed(0)}px（footer 上端 ${footerTop.toFixed(0)}px の ${(-o.over).toFixed(0)}px 手前・推奨 ${L.FOOTER_MARGIN}px）${describe(o.el)}`,
    }));

  // ---- 2. 内側クリップ
  const clipped = [];
  for (const el of all) {
    if (!(el instanceof HTMLElement)) continue;
    const s = style(el);
    if ((s.overflow === 'hidden' || s.overflowY === 'hidden') && el.scrollHeight > el.clientHeight + 1) {
      clipped.push(`scrollHeight=${el.scrollHeight} > clientHeight=${el.clientHeight} ${describe(el)}`);
    }
  }

  // ---- 3. フォント下限
  const fonts = [];
  const fontRaw = [];
  for (const el of all) {
    const txt = textOf(el);
    if (!txt) continue;
    const s = style(el);
    if (!visible(el)) continue;
    const size = parseFloat(s.fontSize);
    if (!(size > 0)) continue;
    const role = roleOf(el);
    const min = role === 'kicker' ? L.FONT_KICKER : role === 'caption' || role === 'badge' ? L.FONT_CAPTION : L.FONT_BODY;
    if (size >= min - 0.01) continue;
    // data-role 無しの救済: 字間の広い英数字ラベルは kicker とみなす
    let level = 'FAIL';
    let note = '';
    if (!role && size >= L.FONT_KICKER) {
      const ls = parseFloat(s.letterSpacing);
      const wide = !Number.isNaN(ls) && ls >= size * 0.1;
      const ascii = /^[\x20-\x7E]+$/.test(txt) && /[A-Za-z0-9]/.test(txt);
      if (wide && ascii) {
        level = 'WARN';
        note = '（字間の広い英数字ラベル＝kicker とみなした。data-role="kicker" を付ける）';
      }
    }
    fontRaw.push({ el, size, min, role, level, note });
  }
  // 同じ文字列を親子で二重に出さない（外側が同程度に小さいなら内側は畳む）
  for (const o of fontRaw) {
    const covered = fontRaw.some((a) => a !== o && a.el.contains(o.el) && a.size <= o.size + 0.01);
    if (covered) continue;
    fonts.push({
      level: o.level,
      msg: `${o.size.toFixed(1)}px < ${o.min}px（${ROLE_LABEL[o.role] || '本文'}）${o.note} ${describe(o.el)}`,
    });
  }

  // ---- 4. 禁止ダッシュ（── U+2500 の 2 連以上 / ― U+2015 / — U+2014）
  const DASH_KINDS = [
    { key: 'box', label: '──', code: 'U+2500x2', re: /\u2500{2,}/g },
    { key: 'horbar', label: '―', code: 'U+2015', re: /\u2015/g },
    { key: 'emdash', label: '—', code: 'U+2014', re: /\u2014/g },
  ];
  const countKinds = (str) => {
    const c = {};
    let total = 0;
    for (const k of DASH_KINDS) {
      const n = (str.match(k.re) || []).length;
      if (n) { c[k.key] = n; total += n; }
    }
    return { c, total };
  };
  const dashes = [];
  const dashByKind = { box: 0, horbar: 0, emdash: 0 };
  let dashCount = 0;
  const seen = new Set();
  for (const el of all) {
    const txt = textOf(el);
    if (!txt) continue;
    const { c, total } = countKinds(txt);
    if (!total) continue;
    dashCount += total;
    for (const k of Object.keys(c)) dashByKind[k] += c[k];
    const key = txt.slice(0, 60);
    if (seen.has(key)) continue;
    seen.add(key);
    if (dashes.length < 5) {
      const kinds = DASH_KINDS.filter((k) => c[k.key]).map((k) => `${k.label} ${k.code}`).join('+');
      dashes.push(`[${kinds}] "${txt.replace(/\s+/g, ' ').slice(0, 60)}"`);
    }
  }
  if (dashCount === 0) {
    const whole = sec.textContent || '';
    const { c, total } = countKinds(whole);
    if (total) {
      dashCount = total;
      for (const k of Object.keys(c)) dashByKind[k] += c[k];
      dashes.push('（テキストノード直下では特定できず。section 全体の textContent で検出）');
    }
  }

  // ---- 5. data-speaker-notes
  const notes = [];
  if (sec.hasAttribute('data-speaker-notes')) {
    notes.push(`section 属性: "${(sec.getAttribute('data-speaker-notes') || '').replace(/\s+/g, ' ').slice(0, 60)}"`);
  }
  sec.querySelectorAll('[data-speaker-notes]').forEach((el) => {
    notes.push(`子孫要素: ${describe(el)}`);
  });

  // ---- 6. アイコン数
  const icons = [];
  sec.querySelectorAll('use').forEach((u) => {
    const href = u.getAttribute('href') || u.getAttribute('xlink:href') || '';
    if (href.startsWith('#ic-')) icons.push(href);
  });

  // ---- 7. 塗りボックス
  const fills = [];
  for (const el of all) {
    if (!(el instanceof HTMLElement)) continue;
    if (footerEl && (footerEl === el || footerEl.contains(el))) continue;
    if (roleOf(el) === 'badge') continue;
    if (!visible(el)) continue;
    const s = style(el);
    if (NEUTRAL_BG.has(s.backgroundColor)) continue;
    if (/^(inline|contents|none)$/.test(s.display)) continue;
    const r = rectOf(el);
    const area = r.width * r.height;
    if (area < L.FILL_MIN_AREA) continue;
    fills.push(`${s.backgroundColor} ${Math.round(r.width)}×${Math.round(r.height)} ${describe(el)}`);
  }

  // ---- 8. 絵文字・アイコンフォント
  // デザインシステムが使う記号（進行表の ▶ ✓、箇条書きの ・、注記の ※、評価の ◎○△ 等）は
  // 絵文字扱いしない。WARN にするのは「絵文字プレゼンテーションで描かれるもの」だけ:
  //   ・U+1F000 以降のピクトグラム（🚀 📌 など）
  //   ・Emoji_Presentation（✅ ❌ ⭐ など既定で絵文字として描かれるもの）
  //   ・異体字セレクタ U+FE0F を伴うもの（⚠️ ▶️ など）
  const pictos = [];
  const ALLOW = new Set([
    '▶', '◀', '▷', '◁', '▲', '▼', '△', '▽',
    '✓', '✔', '✗', '✘', '✕', '✖', '×',
    '◆', '◇', '◎', '○', '●', '■', '□',
    '→', '←', '↑', '↓', '⇒', '⇔',
    '※', '·', '・', '※', '★', '☆', '➕', '➖',
  ]);
  const RE_PICTO = /\p{Extended_Pictographic}/gu;
  const RE_EMOJI_PRES = /\p{Emoji_Presentation}/u;
  const wholeText = sec.textContent || '';
  const found = new Set();
  for (const m of wholeText.matchAll(RE_PICTO)) {
    const ch = m[0];
    if (ALLOW.has(ch)) continue;
    const cp = ch.codePointAt(0);
    const next = wholeText[m.index + ch.length];
    const isEmoji = cp >= 0x1f000 || RE_EMOJI_PRES.test(ch) || next === '\uFE0F';
    if (isEmoji) found.add(ch + (next === '\uFE0F' ? '\uFE0F' : ''));
  }
  if (found.size) pictos.push(`絵文字: ${Array.from(found).join(' ')}`);
  const RE_ICONFONT = /(font\s*awesome|fontawesome|material\s*icons|material\s*symbols|icomoon|glyphicon|ionicons|bootstrap-icons)/i;
  const iconFonts = new Set();
  for (const el of all) {
    if (!textOf(el)) continue;
    const ff = style(el).fontFamily || '';
    if (RE_ICONFONT.test(ff)) iconFonts.add(ff.slice(0, 60));
  }
  for (const ff of iconFonts) pictos.push(`アイコンフォント: ${ff}`);

  return {
    overflowOut,
    footerHits,
    footerTop: footerTop === null ? null : Math.round(footerTop),
    clipped,
    fonts,
    dashes,
    dashCount,
    dashByKind,
    notes,
    iconCount: icons.length,
    icons: Array.from(new Set(icons)),
    fills,
    pictos,
  };
}

// ---------------------------------------------------------------- run

const srv = await startStaticServer({
  root: dirname(filePath),
  fallbackDirs: [resolve(HERE, 'runtime')],
  routes: { [PROBE_ROUTE]: { body: probeHtml, type: 'text/html; charset=utf-8' } },
});

let browser;
let exitCode = 0;
try {
  browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: LIMITS.W, height: LIMITS.H }, deviceScaleFactor: 1 });
  page.setDefaultTimeout(15000);

  await page.goto(srv.origin + PROBE_ROUTE, { waitUntil: 'load' });
  try {
    await page.waitForLoadState('networkidle', { timeout: 15000 });
  } catch {
    // Google Fonts が遅い・落ちている場合でも続行する
  }
  await page.evaluate(() => document.fonts.ready).catch(() => {});

  await page.addStyleTag({ content: PROBE_CSS });
  const meta = await page.evaluate(setupProbe);
  if (!meta.length) {
    console.error('実行エラー: section[data-label] が 0 枚でした');
    process.exit(2);
  }

  let shotsDir = null;
  if (args.shots) {
    shotsDir = resolve(args.shots);
    await mkdir(shotsDir, { recursive: true });
  }

  console.log(`check-slides: ${basename(filePath)} — ${meta.length} sections（オフライン計測 / ${LIMITS.W}×${LIMITS.H}）\n`);

  const results = [];
  let totalFail = 0;
  let totalWarn = 0;

  for (const m of meta) {
    await page.evaluate(mountSection, m.index);
    const r = await page.evaluate(measureMounted, LIMITS);

    const fails = [];
    const warns = [];

    for (const o of r.overflowOut) fails.push(`FAIL はみ出し: ${o}`);
    for (const f of r.footerHits) (f.level === 'FAIL' ? fails : warns).push(`${f.level} ${f.msg}`);
    for (const c of r.clipped) fails.push(`FAIL 内側クリップ: ${c}`);
    for (const f of r.fonts) (f.level === 'FAIL' ? fails : warns).push(`${f.level} フォント下限: ${f.msg}`);
    if (r.dashCount > 0) {
      const bd = [
        ['──', r.dashByKind.box],
        ['―', r.dashByKind.horbar],
        ['—', r.dashByKind.emdash],
      ]
        .filter(([, n]) => n)
        .map(([label, n]) => `${label} ${n}`)
        .join(' / ');
      fails.push(`FAIL 禁止ダッシュの残存: ${r.dashCount} 箇所（${bd}） ${r.dashes.join(' , ')}`);
    }
    for (const n of r.notes) fails.push(`FAIL data-speaker-notes の残存: ${n}`);
    if (r.iconCount > LIMITS.ICON_MAX) {
      warns.push(`WARN アイコン過多: ${r.iconCount} 個（${LIMITS.ICON_MAX + 1} 個以上）${r.icons.join(' ')}`);
    }
    if (r.fills.length > LIMITS.FILL_MAX) {
      warns.push(`WARN 塗りボックス過多: ${r.fills.length} 個（${LIMITS.FILL_MAX + 1} 個以上）\n        ` + r.fills.slice(0, 6).join('\n        '));
    }
    for (const p of r.pictos) warns.push(`WARN ${p}`);

    totalFail += fails.length;
    totalWarn += warns.length;

    const num = String(m.index + 1).padStart(2, '0');
    const mark = fails.length ? '✗' : warns.length ? '△' : '✓';
    console.log(`${mark} [${num}] ${m.label}${m.skip ? ' (data-deck-skip)' : ''}`);
    for (const line of fails) console.log(`    ${line}`);
    for (const line of warns) console.log(`    ${line}`);

    results.push({ index: m.index, num, label: m.label, skip: m.skip, fails, warns, raw: r });

    if (shotsDir) {
      const safe = m.label.replace(/[\/\\:*?"<>|]/g, '_').replace(/\s+/g, '');
      await page.evaluate(() => document.getElementById('dc-probe-host').setAttribute('data-clip', ''));
      await page.screenshot({
        path: resolve(shotsDir, `${num}-${safe}.png`),
        clip: { x: 0, y: 0, width: LIMITS.W, height: LIMITS.H },
      });
      await page.evaluate(() => document.getElementById('dc-probe-host').removeAttribute('data-clip'));
    }
  }

  console.log(`\n${meta.length} sections — FAIL: ${totalFail} / WARN: ${totalWarn}`);
  if (shotsDir) console.log(`スクリーンショット: ${shotsDir}`);

  if (args.json) {
    const jsonPath = resolve(args.json);
    await mkdir(dirname(jsonPath), { recursive: true });
    await writeFile(
      jsonPath,
      JSON.stringify(
        { file: filePath, sections: meta.length, fail: totalFail, warn: totalWarn, results },
        null,
        2
      ),
      'utf8'
    );
    console.log(`JSON: ${jsonPath}`);
  }

  exitCode = totalFail > 0 ? 1 : 0;
} catch (e) {
  console.error('実行エラー:', e && e.stack ? e.stack : e);
  exitCode = 2;
} finally {
  if (browser) await browser.close();
  await srv.close();
}
process.exit(exitCode);

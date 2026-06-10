#!/usr/bin/env node
/**
 * check-slides.mjs — html-slide-deck の Phase 4-5 機械チェック
 *
 * 各 .slide について以下を検査する:
 *   1. 自然高さ: height:auto にしたときの高さが 941px 以下か（余裕 30px 推奨 → 911px 超は警告）
 *   2. 内側クリップ: overflow:hidden な内側要素の scrollHeight が clientHeight を超えていないか
 *   3. 小フォント: テキストを直接持つ要素（SVG text 含む）に 12px 未満が無いか
 *
 * 使い方（playwright-core + インストール済み Google Chrome。ブラウザDL不要）:
 *   npx -y -p playwright-core node check-slides.mjs <path/to/deck.html>
 *
 * 終了コード: 0 = 問題なし（警告のみ含む） / 1 = FAIL あり / 2 = 実行エラー
 */
import { chromium } from 'playwright-core';
import { resolve } from 'node:path';
import { existsSync } from 'node:fs';

const HEIGHT_LIMIT = 941;   // スライド固定高さ
const HEIGHT_MARGIN = 30;   // 投影環境のフォント差を見込む推奨余裕
const MIN_FONT_PX = 12;     // 投影下限

const file = process.argv[2];
if (!file || !existsSync(file)) {
  console.error('usage: npx -y -p playwright-core node check-slides.mjs <deck.html>');
  process.exit(2);
}

const browser = await chromium.launch({ channel: 'chrome', headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1200 } });
  await page.goto('file://' + resolve(file), { waitUntil: 'load' });
  await page.waitForTimeout(300); // Web フォント・スケーラ JS の適用待ち

  const slides = await page.evaluate(({ HEIGHT_LIMIT, MIN_FONT_PX }) => {
    const describe = (el) => {
      const tag = el.tagName.toLowerCase();
      const cls = typeof el.className === 'string' && el.className ? '.' + el.className.trim().split(/\s+/).join('.') : '';
      const id = el.id ? '#' + el.id : '';
      const text = (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 40);
      return `<${tag}${id}${cls}> "${text}"`;
    };
    return Array.from(document.querySelectorAll('.slide')).map((slide, i) => {
      // スケーラ JS の transform を外し、自然高さを実寸で測る
      slide.style.transform = 'none';
      const prev = { height: slide.style.height, overflow: slide.style.overflow };
      slide.style.height = 'auto';
      slide.style.overflow = 'visible';
      const naturalHeight = Math.round(slide.getBoundingClientRect().height);
      slide.style.height = prev.height;
      slide.style.overflow = prev.overflow;

      // 内側クリップ: overflow:hidden 要素の中身が溢れていないか
      const clipped = [];
      for (const el of slide.querySelectorAll('*')) {
        if (!(el instanceof HTMLElement)) continue;
        const cs = getComputedStyle(el);
        if ((cs.overflow === 'hidden' || cs.overflowY === 'hidden') && el.scrollHeight > el.clientHeight + 1) {
          clipped.push(`${describe(el)} scrollHeight=${el.scrollHeight} > clientHeight=${el.clientHeight}`);
        }
      }

      // 小フォント: テキストノードを直接持つ要素 + SVG text
      const smallFonts = new Map();
      const hasDirectText = (el) => Array.from(el.childNodes).some((n) => n.nodeType === 3 && n.textContent.trim());
      for (const el of slide.querySelectorAll('*')) {
        const isSvgText = el.tagName === 'text' || el.tagName === 'tspan';
        if (!isSvgText && !(el instanceof HTMLElement && hasDirectText(el))) continue;
        if (isSvgText && !(el.textContent || '').trim()) continue;
        const size = parseFloat(getComputedStyle(el).fontSize);
        if (size > 0 && size < MIN_FONT_PX) {
          const key = `${size.toFixed(1)}px ${describe(el)}`;
          smallFonts.set(key, (smallFonts.get(key) || 0) + 1);
        }
      }

      return {
        id: slide.id || `slide-${i + 1}`,
        naturalHeight,
        clipped,
        smallFonts: Array.from(smallFonts.keys()),
      };
    });
  }, { HEIGHT_LIMIT, MIN_FONT_PX });

  let fails = 0;
  let warns = 0;
  for (const s of slides) {
    const issues = [];
    if (s.naturalHeight > HEIGHT_LIMIT) {
      issues.push(`FAIL はみ出し: 自然高さ ${s.naturalHeight}px > ${HEIGHT_LIMIT}px`);
      fails++;
    } else if (s.naturalHeight > HEIGHT_LIMIT - HEIGHT_MARGIN) {
      issues.push(`WARN 余裕不足: 自然高さ ${s.naturalHeight}px（推奨 ≤ ${HEIGHT_LIMIT - HEIGHT_MARGIN}px）`);
      warns++;
    }
    for (const c of s.clipped) {
      issues.push(`FAIL 内側クリップ: ${c}`);
      fails++;
    }
    for (const f of s.smallFonts) {
      issues.push(`FAIL 小フォント(<${MIN_FONT_PX}px): ${f}`);
      fails++;
    }
    const mark = issues.some((m) => m.startsWith('FAIL')) ? '✗' : issues.length ? '△' : '✓';
    console.log(`${mark} ${s.id} (自然高さ ${s.naturalHeight}px)`);
    for (const m of issues) console.log(`    ${m}`);
  }

  console.log(`\n${slides.length} slides — FAIL: ${fails} / WARN: ${warns}`);
  process.exit(fails > 0 ? 1 : 0);
} catch (e) {
  console.error('実行エラー:', e.message);
  process.exit(2);
} finally {
  await browser.close();
}

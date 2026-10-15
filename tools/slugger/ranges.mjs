// SPDX-License-Identifier: Apache-2.0 OR MIT
//
// Print the code points github-slugger's regex removes, as the hex ranges
// `_SLUG_REMOVED_RANGES` in reference/blockspec/document.py holds: one token
// per range, `lo-hi` or a lone `cp`, separated by spaces.
//
// The regex is evaluated on every code point, outside the surrogates, so the
// table matches the class code point for code point instead of being read
// off its source. Generated with node v24.20.0 from github-slugger 2.0.0:
//
//   mkdir -p /tmp/slugger && cd /tmp/slugger && npm pack github-slugger@2.0.0 \
//     && tar -xzf github-slugger-2.0.0.tgz
//   node tools/slugger/ranges.mjs /tmp/slugger/package/regex.js
//
// tools/slugger/check.py compares this output with the table in the reference.
import { pathToFileURL } from 'node:url'
import { resolve } from 'node:path'

const { regex } = await import(pathToFileURL(resolve(process.argv[2])).href)
const tokens = []
let start = -1
const flush = (end) => tokens.push(start === end ? start.toString(16) : `${start.toString(16)}-${end.toString(16)}`)
for (let cp = 0; cp <= 0x10ffff; cp++) {
  let removed = false
  if (cp < 0xd800 || cp > 0xdfff) {
    const s = String.fromCodePoint(cp)
    regex.lastIndex = 0
    removed = s.replace(regex, '') !== s
  }
  if (removed && start < 0) start = cp
  if (!removed && start >= 0) { flush(cp - 1); start = -1 }
}
if (start >= 0) flush(0x10ffff)
console.log(tokens.join(' '))

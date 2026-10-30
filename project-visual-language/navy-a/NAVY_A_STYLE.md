# Navy A: SkillMatch house style

Draft 2, 29 October 2026 (document frame corrected to the approved detached-blocks look). Every HTML page in this project uses this style: the app, the website, the graduate guides, the team guides and any one-off page. Layouts can stretch, move and grow to fit their content, but every page must be recognisably Navy A.

**Approved document example (Phil, 29 Oct):** `../github-profile-guide/index.html`, the approved GitHub profile guide and benchmark for this document frame.
**Original colour and tile reference:** the earlier Bento palette study is historical context; its joined guide zone is superseded by the approved Navy A example above.
**Kit:** `navy-a.css` (the stylesheet) and `navy-a-kit.html` (every component rendered; copy it to start a new page).

---

## 1. The taste in one paragraph

Warm stone background. Content sits in separate, soft-cornered off-white blocks that float on it, with stone showing between them. One dark colour, navy slate, carries the weight: the nav pill, the contents box, the one tile that matters most. Headings are black, tight and confident; small labels are mono capitals. Numbers are big. Controls are pills. Blue means a match or a link, never decoration. Nothing touches the edge of the browser, and nothing looks like a government form.

**The recognition test:** put the page next to the approved example above. If it doesn't look like the same product, it isn't finished.

## 2. Colours

| Token | Hex | Use |
|---|---|---|
| `--na-bg` | `#e7e5df` | page background (stone) |
| `--na-surface` | `#faf9f6` | cards |
| `--na-surface-2` | `#efece5` | inner boxes, code briefs, quiet panels |
| `--na-line` | `#e2ded5` | hairlines |
| `--na-ink` | `#161616` | text and headings |
| `--na-muted` | `#68655f` | secondary text on light |
| `--na-panel` | `#2b3a55` | navy slate: the dark surfaces |
| `--na-panel-ink` | `#faf9f6` | text on navy |
| `--na-panel-muted` | `#c3cbdb` | secondary text on navy |
| `--na-accent` | `#3556a8` | links, focus, active states |
| `--na-accent-deep` | `#1e3a8a` | link hover; Strong match |
| `--na-soft-blue` | `#dfe3ec` | notes and advice tiles (text `#1e2a4a`) |
| `--na-code` | `#1f2a3f` | long code and editor panes (text `#e8eef4`) |

**Match tiers (fixed meaning, never reuse for decoration):**
Strong `#1e3a8a` / light text · Good `#3556a8` / light text · Stretch `#a9b8de` / `#1e2a4a` · Not yet `#dfe3ec` / `#1e2a4a`.

**Status:** met `#1f7a4a` · partly `#9a5b12` · gap `#b83b3b`.

**Category dots (guides only, shown as small dots plus a label, never as thick borders):**
GitHub screen `#3556a8` · visual example `#9a5b12` · good practice `#1f7a4a` · privacy and safety `#7d4655`.

No other colours. In particular: no pastels, no orange, no near-black panels.

## 3. Type

- Inter for everything readable; JetBrains Mono for labels and code.
- Headings: Inter 600, tracking -0.03em, black. h1 44–50px, h2 28–32px, h3 17–20px.
- Labels (kickers, phase numbers, image captions, small tags): mono, uppercase, letter-spacing 0.06–0.12em, muted or accent.
- Body 15–16px, line-height about 1.6, lines no longer than about 80 characters.
- Big numbers: Inter 600, 40–84px, tight tracking, with a small muted unit beside them ("7 /8 met").

## 4. Shape and space

- Radius: 26px for cards and tiles, 16px for boxes inside cards, 999px for pills (buttons, nav, tabs, chips, badges).
- No drop shadows and no borders on cards: separation comes from the stone background.
- Page width up to about 1360px, centred, 40px side padding (16px on phones).
- Gaps between tiles 14px; padding inside cards 26–38px.

## 5. Page frames

Every page starts with the **top bar**: the SkillMatch mark (a navy rounded square with "S") and the navy pill nav, with the current page shown as an off-white pill. It uses the real links of the surface it's on. **The "See my matches" button appears on the Find jobs page only.** Guides and every other page have no button on the right.

Then pick one frame:

**A. Document** (guides, READMEs, long explanations). Two things side by side on the stone, with a gap between them:
- **The contents box:** a separate navy box with its own rounded corners. It is only as tall as its contents (title, short line, section links, legend) and ends there, with no empty navy below. It **stays on screen while the reader scrolls**, so the navigation is always visible.
- **The content:** a stack of separate rounded blocks with stone showing in the gaps between them. There is no big cream sheet holding everything. Each phase starts with its own panel (phase pill, heading, intro paragraph); everything after it is its own block: each note, each example card, each set of tiles, each step row, each code box, each expandable row. One-line links are pills.
- Every section of the page uses the same block system, from the first phase to the last. Nothing falls back to flat text running down the page.
- On phones, the contents box becomes a navy strip of sideways-scrolling pills above the content, and the blocks stack.

**B. App screen** (forms, results, dashboards): a grid of mixed-size tiles straight on the stone. One tile is navy and large (the hero); counts are big-number tiles; the rest are off-white.

**C. Short page** (about, sources, a single message): a stack of blocks, no contents box.

**Never:**
- a full-height sidebar or a navy column joined to the content
- one big sheet holding the whole document
- flat, unboxed text sections
- an old layout recoloured

## 6. Content to component

| The content is… | Use |
|---|---|
| the start of a phase or section | its own panel: navy phase pill with white text, heading, intro paragraph |
| a one-line link or pointer ("Want to see how…?") | a pill link |
| a closing remark or aside | a quiet stone-tinted block |
| a group of key points (e.g. "four things to make visible") | a row of tiles led by one navy tile carrying the group's title |
| a sequence of steps | step rows: rounded pill rows with a number circle, title and status on the right. **The step's text always goes in one wrapper `<div>`** so links, bold and code flow inline and wrap; extras for a step (an example box, a screenshot) go below the sentence, full width, never beside it as a column |
| a short command, Markdown sample or text to copy | job-brief box: light mono box on `--na-surface-2`, with a Copy pill button when useful |
| a long code or editor view | dark code pane `--na-code` |
| advice, a caveat, "why this matters" | pale-blue note tile |
| the one thing that must stand out | navy tile, sparingly (one per screen at most) |
| a handful of facts or counts | big-number tiles in a grid |
| a set of choices or views | pill tabs |
| tools, skills, tags | chips |
| a match level | tier badge (pill with a dot) |
| a status on a line | ✓ met / ~ partly / ✕ gap in status colours |
| examples to compare | example cards: image on top, mono label, bold title, one muted line |
| a picture that needs explaining | figure card: image, then caption on `--na-surface-2`; click to enlarge |
| optional depth | details/summary in an off-white card, summary in accent blue |
| a checklist | pill rows with a navy tick |
| a comparison | two cards side by side, or a simple table with hairlines, no zebra stripes |

A diagram is worth adding only when it explains something the text can't. No decorative pictures.

## 7. Imitating other platforms

When a page shows a mock-up of someone else's interface (a GitHub profile, a LinkedIn page, a settings screen), that mock keeps the platform's own colours and look, inside a figure card. Our style frames it; it doesn't repaint it.

## 8. The app

The app's `../../prototype/app/skillmatch/web/static/tokens.css` keeps its own token names. To bring it into Navy A, change the values only:

| App token | Navy A value |
|---|---|
| `--paper` | `#e7e5df` |
| `--paper-raised` | `#faf9f6` |
| `--ink` | `#161616` |
| `--ink-soft` | `#68655f` |
| `--rule` | `#e2ded5` |
| `--accent` | `#3556a8` |
| `--accent-hover` | `#1e3a8a` |
| `--accent-wash` | `#dfe3ec` |
| `--tier-strong` / `-good` / `-stretch` / `-not-yet` | `#1e3a8a` / `#3556a8` / `#a9b8de` / `#dfe3ec` |
| `--serif`, `--sans` | Inter (load it); serif headings are not Navy A |

Then add the navy panel, radii and pills in `../../prototype/app/skillmatch/web/static/site.css`. Check the map: the two lighter tiers need a dark outline on map markers to stay visible.

## 9. How a page gets made

1. Codex shapes the content (clarity-first) and marks up what each part is: steps, notes, examples, code, figures. It can arrive as Markdown or HTML.
2. Claude (Robert) picks the frame, maps each part to a component from section 6, and builds the page on `navy-a.css`, starting from a copy of `navy-a-kit.html`.
3. The wording stays as Codex wrote it. Restyling never rewrites content.

## 10. Checks before anything goes out

- Side by side with the reference image: does it look like the same product?
- Text contrast at least 4.5:1 (3:1 for large text). Fix by changing the text colour, not the background.
- Rendered at 1440 and 390 wide: no sideways scroll on phones, contents usable.
- Links, enlargeable images, details and anchors all work.
- Only Navy A colours, apart from mock-ups of other platforms.

## 11. Decisions and why (29 October 2026)

These came from Phil reviewing real pages. Each one is a rule now; the reason is what to apply to cases the rules don't cover.

**The underlying idea:** every piece of content is an object you can see the edges of. A reader should be able to scan the page as a set of distinct, rounded things on stone, and know what each one is from its shape and colour before reading it. Anything that blurs those edges (flat text, one big sheet, things that merge) is wrong, even when it's tidy.

| Decision | Why |
|---|---|
| Navigation is its own rounded navy box, only as tall as its contents, and stays on screen while scrolling | A full-height navy column reads as a separate page bolted on, and its empty lower half is dead weight. A box that travels with you is always useful and never looms. |
| No single cream sheet behind the content; separate blocks with stone gaps | One sheet turns the page back into a document. The gaps are what make it Navy A. |
| Every section uses the same block system, top to bottom | A page that starts in blocks and drifts into flat text looks unfinished. Consistency is the style. |
| Phase pills are navy with white text (Step 4d) | Grey on grey on cream disappeared. Phase starts are landmarks; they echo the navigation's navy so a reader scrolling fast can see where each phase begins. |
| A step's text sits in one wrapper; extras (an example box, a screenshot) go below the sentence, full width | Inline links, bold and code must read as a sentence. Putting extras beside the text squeezed it into unreadable columns. |
| Paired labels ("What you type" / "Markdown source") sit apart: one left, one right | Run together they read as gibberish. |
| Code inside a code box takes the box's colours; light code boxes keep dark text even inside navy tiles | Readability beats consistency of a component: a style that hides text has failed. |
| Imitations of another platform (GitHub, LinkedIn) keep that platform's look, framed inside a rounded figure block | They show readers what the real thing looks like; our frame says "this is an example", their colours say "this is what you'll see". |
| Very tall screenshots show their top at about 640px; the lightbox opens the full image | A giant image breaks the rhythm of blocks and buries what follows. |
| "Click to enlarge" sits below the image, not on it | It must never cover the thing it invites you to look at. |
| Figures fill the width of the content column; related figures stack rather than sit side by side at uneven sizes | Uneven pairs look accidental, and small images become unreadable. |
| Cards placed side by side as a pair are equal height | Ragged pairs look unfinished. |
| Long lists (sources) split into two columns on desktop | A single very long panel becomes a wall. |
| "See my matches" appears only on the Find jobs page | Buttons belong where their action makes sense; guides aren't the place to push matching. |
| Colours have fixed meanings: navy carries weight, blue means a match or a link, category dots mean guide categories | If a colour is used for decoration it stops meaning anything. |

When a new case comes up, ask: can the reader see the edges of each thing, and does each thing look like what it is? If not, it isn't Navy A yet.

Balanced rows. In a two-column bento row, both columns must end level. If one side is shorter, add a related, useful visual panel under it (a real screenshot, chart or example), or stack the boxes full width. Never leave an empty hole. Every filler must teach something relevant to that section; no decoration.

Fit the space that exists. Measure both columns before adding anything, and size the filler to the gap. A filler must not push other boxes or create a new gap; after any change, recheck every column in the row and the rows around it. Prefer making the shorter panel's content richer and evenly spaced over adding a new box. Fillers carry useful content for that section, never credits, decoration or empty padding.

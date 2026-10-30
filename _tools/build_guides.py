"""Build the live SkillMatch team guides in Navy A from the content modules."""
import html
import pathlib
import sys

from bs4 import BeautifulSoup, Tag

OUT = pathlib.Path(sys.argv[1])

PAGES = [
    ("a1-get-skillmatch.html", "A1", "Get SkillMatch onto your machine"),
    ("a2-switch-on-the-ai.html", "A2", "Pick your AI assistant"),
    ("a3-add-your-folder.html", "A3", "Add your folder"),
    ("a4-send-it-for-review.html", "A4", "Send it for review"),
]
BPAGES = [
    ("b1-the-big-picture.html", "B1", "The big picture"),
    ("b2-your-copy-and-the-shared-copy.html", "B2", "Your copy and the shared copy"),
    ("b3-add-files-to-the-repository.html", "B3", "Add files to the repository"),
    ("b4-open-a-pull-request-properly.html", "B4", "Open a pull request, properly"),
    ("b5-cards-and-closes.html", "B5", "Cards, numbers and 'Closes'"),
    ("b6-glossary.html", "B6", "Glossary"),
]
CPAGES = [("c3-how-skillmatch-finds-the-jobs.html", "C3", "How SkillMatch finds the jobs")]
DPAGES = [
    ("d1-start-from-the-latest.html", "D1", "Start from the latest"),
    ("d2-make-a-branch.html", "D2", "Make a branch for your card"),
    ("d3-save-and-upload.html", "D3", "Save and upload"),
    ("d4-open-a-pull-request.html", "D4", "Open a pull request"),
    ("d5-after-its-merged.html", "D5", "After it's merged"),
]
EPAGES = [
    ("e1-review-a-pull-request.html", "E1", "Review a pull request"),
    ("e2-merge-it.html", "E2", "Merge it"),
    ("e3-when-theres-a-conflict.html", "E3", "When there's a conflict"),
    ("e4-protect-main.html", "E4", "Protect main"),
]
HELP = ("help.html", "?", "Stuck? Help and other routes")
GROUPS = [
    ("Getting started", "GET SET UP", PAGES),
    ("Understanding GitHub", "GITHUB BASICS", BPAGES),
    ("Vacancy data", "VACANCY DATA", CPAGES),
    ("Working on a task", "TASKS", DPAGES),
    ("Reviewing and merging", "REVIEWS", EPAGES),
]


def page_group(current):
    for title, kicker, pages in GROUPS:
        if current in [p[0] for p in pages]:
            return title, kicker, pages
    return "Help", "HELP", [HELP]


def contents(current):
    group_title, _, pages = page_group(current)
    out = [f'<aside class="na-contents na-guide-contents" aria-label="{html.escape(group_title)}">',
           f'<h2>{html.escape(group_title)}</h2>', '<ol>']
    for fname, number, title in pages:
        current_attr = ' aria-current="page"' if fname == current else ""
        out.append(
            f'<li><a href="{fname}"{current_attr}><b>{number}</b><span>{html.escape(title)}</span></a></li>'
        )
    if len(pages) == 1:
        out.append('<li><a href="index.html"><span>Back to the team hub</span></a></li>')
    out.extend(['</ol>', '</aside>'])
    return "\n".join(out)


def series(current):
    return page_group(current)[2]


def pager(current):
    pages = series(current)
    files = [p[0] for p in pages]
    titles = {p[0]: p[2] for p in pages}
    i = files.index(current)
    prev = (files[i - 1], titles[files[i - 1]]) if i else ("index.html", "Team hub")
    nxt = (files[i + 1], titles[files[i + 1]]) if i + 1 < len(files) else ("index.html", "Team hub")
    return (
        '<nav class="na-guide-pager" aria-label="Previous and next guide">'
        f'<a href="{prev[0]}">← Previous: {html.escape(prev[1])}</a>'
        f'<a href="{nxt[0]}">Next: {html.escape(nxt[1])} →</a>'
        '</nav>'
    )


def add_classes(tag, *names):
    current = list(tag.get("class", []))
    for name in names:
        if name not in current:
            current.append(name)
    tag["class"] = current


def transform_body(markup, stem):
    """Map the content modules' semantic HTML onto the Navy A component set."""
    soup = BeautifulSoup(markup, "html.parser")
    command_number = 0

    def transform(node):
        nonlocal command_number
        if not isinstance(node, Tag):
            return
        classes = set(node.get("class", []))

        if node.name == "section" and "keypoints" in classes:
            heading = node.find("h2", recursive=False)
            listing = node.find(["ul", "ol"], recursive=False)
            items = listing.find_all("li", recursive=False) if listing else []
            if heading is not None and len(items) >= 2:
                grid = soup.new_tag("div", attrs={"class": ["na-tiles", "na-guide-keypoints"]})
                lead = soup.new_tag("article", attrs={
                    "class": ["na-tile", "na-tile--navy", "na-guide-keypoint-lead"]
                })
                title = soup.new_tag("h3")
                for child in list(heading.contents):
                    title.append(child.extract())
                lead.append(title)
                grid.append(lead)
                for item in items:
                    tile = soup.new_tag("article", attrs={"class": ["na-tile", "na-guide-keypoint"]})
                    for child in list(item.contents):
                        tile.append(child.extract())
                    grid.append(tile)
                node.replace_with(grid)
                return
            node.name = "section"
            node["class"] = ["na-panel", "na-guide-keypoint-note"]

        if node.name == "div" and "cmd" in classes:
            command_number += 1
            text = node.get_text("", strip=False).strip("\n")
            code_class = "na-codepane" if "code" in classes else "na-brief"
            target_id = f"copy-{stem}-{command_number}"
            box_classes = ["na-command", code_class]
            if code_class == "na-codepane":
                box_classes.append("na-command--code")
            box = soup.new_tag("div", attrs={"class": box_classes})
            button = soup.new_tag("button", attrs={
                "type": "button",
                "class": ["na-btn", "na-guide-copy"],
                "data-copy-target": target_id,
            })
            button.string = "Copy"
            pre = soup.new_tag("pre", attrs={"class": ["na-command-text"], "id": target_id})
            pre.string = text
            box.append(button)
            box.append(pre)
            node.replace_with(box)
            return

        if node.name == "div" and "promptbox" in classes:
            node["class"] = ["na-command", "na-brief", "na-command--prompt"]
            button = node.select_one("button#copyBtn")
            pre = node.select_one("pre#prompt")
            if button:
                add_classes(button, "na-btn", "na-guide-copy")
            if pre:
                pre["class"] = ["na-command-text"]

        if node.name == "div" and "picker" in classes:
            add_classes(node, "na-chips", "na-guide-picker")
            for button in node.select("button"):
                add_classes(button, "na-btn", "na-btn--ghost", "na-guide-choice")

        if node.name == "ol" and "do" in classes:
            node["class"] = ["na-steps", "na-steps--long"]
            for item in node.find_all("li", recursive=False):
                item["class"] = ["na-step"]
                wrapper = soup.new_tag("div")
                for child in list(item.contents):
                    wrapper.append(child.extract())
                item.append(wrapper)
                for child in list(wrapper.contents):
                    transform(child)
            return

        if node.name == "div" and "flow" in classes:
            node["class"] = ["na-tiles", "na-guide-flow"]
            for box in node.select(".box"):
                box["class"] = ["na-tile", "na-guide-flow-tile"]
            for who in node.select(".who"):
                add_classes(who, "na-guide-who")

        if node.name == "figure":
            add_classes(node, "na-figure")
            if "stack" in classes:
                add_classes(node, "na-figure--stack")
                for place in node.select(".place"):
                    add_classes(place, "na-stack-place")
                for arrow in node.select(".link"):
                    add_classes(arrow, "na-stack-link")

        if node.name == "dl" and "gloss" in classes:
            table = soup.new_tag("table", attrs={"class": ["na-table", "na-glossary"]})
            tbody = soup.new_tag("tbody")
            table.append(tbody)
            for term in node.find_all("dt", recursive=False):
                description = term.find_next_sibling("dd")
                row = soup.new_tag("tr")
                heading = soup.new_tag("th", attrs={"scope": "row"})
                detail = soup.new_tag("td")
                for child in list(term.contents):
                    heading.append(child.extract())
                if description:
                    for child in list(description.contents):
                        detail.append(child.extract())
                row.append(heading)
                row.append(detail)
                tbody.append(row)
            node.replace_with(table)
            return

        if node.name == "details":
            node["class"] = ["na-details"]
            summary = node.find("summary", recursive=False)
            if summary:
                content = []
                after_summary = False
                for child in list(node.contents):
                    if child is summary and not after_summary:
                        after_summary = True
                        continue
                    if after_summary:
                        content.append(child)
                if content:
                    wrapper = soup.new_tag("div")
                    for child in content:
                        wrapper.append(child.extract())
                    node.append(wrapper)

        if node.name == "table":
            add_classes(node, "na-table")

        if node.name == "span" and "pill" in classes:
            flavor = next((value for value in ("built", "wait", "todo", "skip") if value in classes), "todo")
            node["class"] = ["na-badge", f"na-guide-badge--{flavor}"]
            return

        if node.name == "ul" and "tally" in classes:
            node["class"] = ["na-chips", "na-guide-tally"]
            for item in node.find_all("li", recursive=False):
                item["class"] = ["na-chip", "na-guide-tally-item"]
            return

        if node.name == "p" and ("callout" in classes or "aside" in classes):
            node.name = "aside"
            node["class"] = ["na-note"]
        elif node.name == "p" and "done-when" in classes:
            node["class"] = ["na-panel", "na-panel--quiet", "na-guide-done"]

        for child in list(node.contents):
            transform(child)

    for child in list(soup.contents):
        transform(child)

    def is_component(node):
        if not isinstance(node, Tag):
            return False
        classes = set(node.get("class", []))
        return (
            node.name == "h2"
            or node.name in {"ol", "table", "figure", "details", "aside", "blockquote", "svg"}
            or any(name in classes for name in ("na-command", "na-tiles", "na-note", "na-guide-done"))
            or node.name == "section" and "na-panel" in classes
        )

    def is_plain(node):
        return isinstance(node, Tag) and node.name in {"p", "h3", "h4", "ul", "pre"} and not is_component(node)

    nodes = [node for node in list(soup.contents) if isinstance(node, Tag) or str(node).strip()]
    output = []
    pending = []

    def flush_plain():
        if pending:
            panel = soup.new_tag("section", attrs={"class": ["na-panel"]})
            for node in pending:
                panel.append(node)
            output.append(panel)
            pending.clear()

    i = 0
    while i < len(nodes):
        node = nodes[i]
        if isinstance(node, Tag) and node.name == "h2":
            flush_plain()
            group = [node]
            i += 1
            if i < len(nodes) and isinstance(nodes[i], Tag) and nodes[i].name != "h2":
                if is_plain(nodes[i]):
                    while i < len(nodes) and is_plain(nodes[i]):
                        group.append(nodes[i])
                        i += 1
                else:
                    group.append(nodes[i])
                    i += 1
            panel = soup.new_tag("section", attrs={"class": ["na-panel"]})
            for item in group:
                panel.append(item)
            output.append(panel)
            continue
        if (
            isinstance(node, Tag)
            and node.name == "aside"
            and "na-note" in node.get("class", [])
            and node.find("strong", recursive=False)
            and node.find("strong", recursive=False).get_text(" ", strip=True).startswith("Prefer your AI assistant to do it?")
            and i + 1 < len(nodes)
            and isinstance(nodes[i + 1], Tag)
            and "na-command" in nodes[i + 1].get("class", [])
        ):
            flush_plain()
            node.append(nodes[i + 1])
            output.append(node)
            i += 2
            continue
        if is_component(node):
            flush_plain()
            if isinstance(node, Tag) and node.name == "table":
                panel = soup.new_tag("section", attrs={"class": ["na-panel"]})
                panel.append(node)
                output.append(panel)
            else:
                output.append(node)
            i += 1
            continue
        pending.append(node)
        i += 1
    flush_plain()
    return "\n".join(str(node) for node in output)


def page(fname, num, title, standfirst, body, extra_script=""):
    group_title, group_kicker, _ = page_group(fname)
    kicker = f"{num} · {group_kicker}" if num != "?" else "HELP"
    guide_body = transform_body(body, pathlib.Path(fname).stem)
    doc = f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{html.escape(title)} · SkillMatch team guides</title>
<meta name="description" content="{html.escape(standfirst)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap">
<link rel="icon" type="image/png" href="../assets/img/favicon.png">
<link rel="stylesheet" href="../project-visual-language/navy-a/navy-a.css">
<style>
.guide-brand{{display:flex;align-items:center;gap:10px}}
.guide-team-label{{font-size:11px;color:var(--na-muted)}}
.guide-nav{{flex:0 1 auto}}
.na-guide-layout{{max-width:1360px}}
.na-guide-opening{{padding:26px 30px}}
.na-guide-opening .na-phase-head{{margin:0 0 10px}}
.na-guide-opening h1{{font-size:clamp(30px,3.5vw,42px);max-width:24ch;margin:0 0 8px}}
.na-guide-opening p{{margin:0;color:var(--na-muted);font-size:16px;line-height:1.5;max-width:76ch}}
.na-guide-contents>h2{{margin-bottom:10px}}
.na-guide-contents li a{{align-items:flex-start}}
.na-guide-contents li a b{{flex:none}}
.na-guide-article{{min-width:0}}
.na-guide-article>.na-panel,.na-guide-article>.na-panel--quiet{{margin:0}}
.na-guide-article>.na-figure{{margin:0}}
.na-guide-article>.na-details{{margin:0}}
.na-guide-article>.na-steps{{margin:0}}
.na-guide-article>.na-tiles{{margin:0}}
.na-guide-article>.na-command{{margin:0}}
.na-guide-article>.na-panel>p:first-child{{margin-top:0}}
.na-guide-article .na-step>div>strong:first-child{{display:block;margin-bottom:4px}}
.na-guide-article .na-step>div{{flex:1;width:100%;min-width:0}}
.na-guide-done{{margin:0}}
.na-command{{position:relative;display:block;min-width:0}}
.na-command.na-brief{{margin:0;padding:52px 96px 16px 18px;border:1px solid var(--na-line);border-radius:var(--na-r-sm);background:var(--na-surface-2);color:var(--na-ink);font:13px/1.6 var(--na-mono);overflow-wrap:anywhere}}
.na-command.na-codepane{{margin:0;padding:52px 96px 16px 18px;border:1px solid var(--na-code);border-radius:var(--na-r-sm);background:var(--na-code);color:var(--na-code-ink);font:13px/1.7 var(--na-mono);overflow:visible}}
.na-command-text{{display:block;margin:0;padding:0;border:0;border-radius:0;background:transparent;color:inherit;font:inherit;line-height:inherit;white-space:pre-wrap;overflow-wrap:anywhere}}
.na-command .na-guide-copy{{position:absolute;top:8px;right:8px;z-index:1;margin:0;font-size:12px;padding:7px 14px;border:1px solid var(--na-panel);background:var(--na-panel);color:var(--na-panel-ink)}}
.na-command--code .na-guide-copy{{border-color:var(--na-panel-ink)}}
.na-note .na-command{{margin-top:12px}}
.na-guide-picker{{margin:10px 0}}
.na-guide-picker .na-btn{{border-color:var(--na-muted)}}
.na-guide-picker [aria-pressed=true]{{background:var(--na-panel);border-color:var(--na-panel);color:var(--na-panel-ink)}}
.na-guide-flow{{grid-template-columns:repeat(auto-fit,minmax(170px,1fr));align-items:stretch}}
.na-guide-flow .na-tile{{min-width:0;min-height:0;justify-content:flex-start;align-items:flex-start;gap:6px;padding:16px}}
.na-guide-flow-tile{{overflow-wrap:anywhere}}
.na-guide-flow .who,.na-guide-who{{margin-top:4px;color:var(--na-muted);font:600 11px/1.35 var(--na-mono)}}
.na-guide-keypoints{{grid-template-columns:repeat(auto-fit,minmax(170px,1fr));align-items:stretch}}
.na-guide-keypoints .na-tile{{min-width:0;min-height:0;justify-content:flex-start;align-items:flex-start;padding:16px;overflow-wrap:anywhere}}
.na-guide-keypoint-lead h3{{color:var(--na-panel-ink)}}
.na-figure--stack{{padding:18px}}
.na-stack-place{{display:flex;flex-direction:column;gap:4px;padding:14px 16px;border-radius:var(--na-r-sm);background:var(--na-surface-2)}}
.na-stack-link{{display:flex;justify-content:space-between;gap:12px;padding:5px 10px;color:var(--na-muted);font:600 11px/1.35 var(--na-mono);text-align:center}}
.na-details .ct{{margin-left:6px;color:var(--na-muted);font-weight:500}}
.na-guide-badge--built{{background:var(--na-good);color:#faf9f6}}
.na-guide-badge--wait{{background:var(--na-soft-blue);color:var(--na-soft-blue-ink)}}
.na-guide-badge--todo{{background:var(--na-surface-2);color:var(--na-ink)}}
.na-guide-badge--skip{{background:var(--na-surface);color:var(--na-muted)}}
.na-guide-article .na-badge{{border:1px solid var(--na-panel);padding:5px 10px}}
.na-guide-article .na-chip{{border-color:var(--na-muted)}}
.na-glossary th{{width:18%;font:700 15px/1.5 var(--na-sans);letter-spacing:0;text-transform:none;color:var(--na-ink)}}
.na-guide-article table{{max-width:100%}}
.na-guide-article th,.na-guide-article td{{overflow-wrap:anywhere;vertical-align:top}}
.na-guide-article code{{overflow-wrap:anywhere}}
.na-guide-pager{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}}
.na-guide-pager a{{display:flex;align-items:center;justify-content:center;min-width:0;min-height:56px;padding:12px 18px;border:1px solid var(--na-muted);border-radius:var(--na-pill);background:var(--na-surface-2);color:var(--na-ink);font-weight:600;line-height:1.35;text-align:center;text-decoration:none}}
.na-guide-pager a:hover{{background:var(--na-surface);border-color:var(--na-accent);color:var(--na-ink)}}
.na-guide-footer{{max-width:none;margin:0;padding:8px 0 16px;display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}}
.na-guide-footer p{{margin:0}}
.na-guide-footer .na-pill-link{{padding:8px 14px;background:var(--na-surface-2);border:1px solid var(--na-muted);color:var(--na-ink);text-decoration:none}}
.na-guide-footer .na-pill-link:hover{{background:var(--na-surface);border-color:var(--na-accent);color:var(--na-ink)}}
@media(max-width:850px){{
  .guide-nav{{display:grid;grid-template-columns:repeat(2,max-content);justify-content:center;overflow:visible}}
  .na-guide-contents>h2{{display:none}}
  .na-guide-contents ol{{margin:0}}
  .na-guide-contents li a{{border-color:rgba(250,249,246,.65)}}
  .na-guide-flow{{grid-template-columns:repeat(2,minmax(0,1fr))}}
  .na-guide-keypoints{{grid-template-columns:repeat(2,minmax(0,1fr))}}
  .na-guide-pager{{grid-template-columns:1fr}}
  .na-guide-footer{{padding:8px 0 12px}}
}}
@media(max-width:560px){{
  .na-guide-opening{{padding:20px 18px}}
  .na-guide-opening .na-phase-head{{margin-bottom:8px}}
  .na-guide-flow,.na-guide-keypoints{{grid-template-columns:1fr}}
  .na-stack-link{{flex-direction:column;gap:2px}}
  .na-command.na-brief,.na-command.na-codepane{{padding:52px 82px 16px 14px}}
  .na-glossary,.na-glossary tbody{{display:block;width:100%}}
  .na-glossary tr{{display:block;margin:0 0 8px;padding:10px 12px;border:1px solid var(--na-muted);border-radius:var(--na-r-sm);background:var(--na-surface-2)}}
  .na-glossary th,.na-glossary td{{display:block;width:auto;padding:4px 0;border:0;text-align:left}}
  .na-glossary th{{font-size:15px}}
  .na-glossary td{{padding-top:0}}
}}
</style>
</head>
<body class="na-guide">
<a class="na-skip" href="#main">Skip to content</a>
<header class="na-top na-top--document">
  <div class="guide-brand">
    <a class="na-mark" href="index.html"><i aria-hidden="true">S</i>SkillMatch</a>
    <span class="na-label guide-team-label">TEAM</span>
  </div>
  <nav class="na-nav guide-nav" aria-label="Main">
    <a href="index.html">Team hub</a>
    <a href="../">Public site</a>
    <a href="https://skillmatch-926015010605.europe-west2.run.app">Find jobs</a>
    <a href="https://github.com/users/TidyWeb/projects/3">Project board</a>
  </nav>
</header>
<main class="na-page na-page--document na-layout na-guide-layout" id="main">
{contents(fname)}
<article class="na-flow na-guide-article" id="guide-content">
  <section class="na-panel na-hero na-guide-opening" aria-labelledby="page-title">
    <div class="na-phase-head"><span class="na-label">{html.escape(kicker)}</span></div>
    <h1 id="page-title">{html.escape(title)}</h1>
    <p>{html.escape(standfirst)}</p>
  </section>
{guide_body}
{pager(fname)}
  <footer class="na-footer na-guide-footer">
    <a class="na-pill-link" href="archive/2026-10-30_before_navy_a/README.md">Archive: how the project developed <b aria-hidden="true">→</b></a>
    <p>Phil · John · SK · Esmat · Oana</p>
  </footer>
</article>
</main>
<script>
document.addEventListener("click", async (event) => {{
  const button = event.target.closest("[data-copy-target]");
  if (!button) return;
  const target = document.getElementById(button.dataset.copyTarget);
  if (!target) return;
  try {{
    await navigator.clipboard.writeText(target.innerText || target.textContent);
    button.textContent = "Copied";
    button.dataset.copyStatus = "copied";
  }} catch (_error) {{
    const range = document.createRange();
    range.selectNodeContents(target);
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    button.textContent = "Selected: press Ctrl+C";
    button.dataset.copyStatus = "selected";
  }}
}});
</script>
{extra_script}
</body>
</html>
"""
    (OUT / fname).write_text(doc, encoding="utf-8")


source = pathlib.Path(sys.argv[2])
exec(compile(source.read_text(encoding="utf-8"), str(source), "exec"), globals())

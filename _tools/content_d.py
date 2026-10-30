
def ai(prompt):
    return ('<p class="aside"><strong>Prefer your AI assistant to do it?</strong> Paste this into whichever one you use:</p>'
            f'<div class="cmd">{prompt}</div>')

page("d1-start-from-the-latest.html", "D1", 'Start from the latest',
     "Before every task, bring your copy up to date with the team's shared version. One minute.",
     """<p class="aside"><strong>Before this guide:</strong> SkillMatch must already be on your computer. That means you have made a projects folder and cloned the repository into it, which is <a href="a1-get-skillmatch.html">A1</a>. If you haven't, do A1 first. This guide won't work without it.</p>
<ol class="do">
<li><strong>Open SkillMatch in VS Code</strong>
<strong>File → Open Recent</strong> → SkillMatch. If it isn't in the list, choose <strong>File → Open Folder</strong> instead and pick the <code>SkillMatch</code> folder inside your projects folder.</li>
<li><strong>Switch to main</strong>
Click the branch name in the bottom-left corner and choose <code>main</code>.</li>
<li><strong>Pull</strong>
Source Control → <strong>…</strong> → <strong>Pull</strong>. This downloads everything teammates have had merged.</li>
</ol>
<p class="aside"><strong>Prefer your AI assistant to do it?</strong> Paste this into whichever one you use:</p>
<div class="cmd">Switch this repository to main and pull the latest changes. Tell me if anything is uncommitted first, and don't discard it.</div>
<p class="done-when"><strong>Done when:</strong> the bottom-left says <code>main</code> and Pull reports nothing new, or has finished downloading.</p>""")

page("d2-make-a-branch.html", "D2", 'Make a branch for your card',
     "Give each task its own lane, named after its card on the board. Nothing you do there changes anyone else's work.",
     """<ol class="do">
<li><strong>Find your card's number</strong>
On the <a href="https://github.com/users/TidyWeb/projects/3">project board</a>, open your card. The number is next to its title, e.g. <code>#24</code>.</li>
<li><strong>Create the branch</strong>
Click the branch name in the bottom-left → <strong>Create new branch…</strong> → type the number and a few words, with hyphens:
<div class="cmd">24-interface-feedback</div></li>
<li><strong>Check you're on it</strong>
The bottom-left now shows your branch name. Work only here, never on <code>main</code>. GitHub won't accept changes pushed straight to <code>main</code> anyway.</li>
</ol>
<p class="aside"><strong>Prefer your AI assistant to do it?</strong> Paste this into whichever one you use:</p>
<div class="cmd">Create and switch to a new branch called 24-interface-feedback, starting from an up-to-date main.</div>
<p class="done-when"><strong>Done when:</strong> the bottom-left shows your new branch name.</p>""")

page("d3-save-and-upload.html", "D3", 'Save and upload',
     'Save your work as a checkpoint (a commit), then upload your branch to GitHub. Do it at least once a day.',
     """<ol class="do">
<li><strong>Make your change and save the files</strong></li>
<li><strong>Choose what goes in</strong>
In Source Control, look at <strong>Changes</strong>. Click <strong>+</strong> beside only the files you meant to change.</li>
<li><strong>Commit with a clear message</strong>
Say what you did, in plain words, then click <strong>Commit</strong>:
<div class="cmd">Add vacancy source research notes</div></li>
<li><strong>Upload</strong>
Click <strong>Publish Branch</strong> the first time, then <strong>Sync Changes</strong> after that.</li>
</ol>
<p class="aside"><strong>Prefer your AI assistant to do it?</strong> Paste this into whichever one you use:</p>
<div class="cmd">Show me what has changed. Stage only the files I confirm, commit them with a short plain-English message I approve, and push this branch. Never push to main or force-push.</div>
<p class="done-when"><strong>Done when:</strong> Source Control shows no outstanding changes, and your branch appears on GitHub.</p>""")

page("d4-open-a-pull-request.html", "D4", 'Open a pull request',
     'Ask for your branch to be checked and added to the shared version. Linking it to your card moves the card for you.',
     """<ol class="do">
<li><strong>Start it on GitHub</strong>
Open <a href="https://github.com/TidyWeb/SkillMatch">the repository</a> and click <strong>Compare &amp; pull request</strong> on the yellow banner. (No banner? <strong>Pull requests → New pull request</strong>, and choose your branch.)</li>
<li><strong>Check the direction</strong>
<strong>base: main</strong> ← <strong>compare: your branch</strong>.</li>
<li><strong>Describe it</strong>
Title: what it does. Description: what you changed and why, ending with this line, using your card's number:
<div class="cmd">Closes #24</div></li>
<li><strong>Ask for a review and create it</strong>
Under <strong>Reviewers</strong>, choose Phil (or the agreed reviewer), then <strong>Create pull request</strong>.</li>
</ol>
<p class="done-when"><strong>Done when:</strong> your pull request is open and shows a reviewer. When it's merged, your card moves to Done by itself.</p>""")

page("d5-after-its-merged.html", "D5", "After it's merged",
     'Get the merged version back onto your computer and clear away the old branch, ready for the next card.',
     """<p><strong>Asked for changes first?</strong> Make them on the same branch, commit and Sync (D3). The pull request updates itself, so there's no need for a new one.</p>
<ol class="do">
<li><strong>Back to main and pull</strong>
Exactly as in <a href="d1-start-from-the-latest.html">D1</a>. Your work now arrives as part of <code>main</code>.</li>
<li><strong>Delete the old branch on your computer</strong>
<code>Ctrl+Shift+P</code> (Mac <code>Cmd+Shift+P</code>) → <strong>Git: Delete Branch…</strong> → choose it. GitHub deletes its copy automatically.</li>
<li><strong>Next card</strong>
Start again at D1.</li>
</ol>
<p class="done-when"><strong>Done when:</strong> you're on an up-to-date <code>main</code> and the old branch is gone.</p>""")

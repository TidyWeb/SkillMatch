page("a1-get-skillmatch.html", "A1", 'Get SkillMatch onto your machine',
     "Put a copy of the team repository on the computer you've used for the course, in its own folder. About 5 minutes.",
     """<p><strong>First:</strong> accept Phil's invitation to TidyWeb/SkillMatch (it's in your email, or at <a href="https://github.com/notifications">github.com/notifications</a>). Without it you can look, but you can't upload.</p>
<ol class="do">
<li><strong>Make a folder to hold your projects</strong>
In your file manager (File Explorer on Windows, Finder on Mac), use the folder where you keep your course projects. If you don't have one, make a new folder called <code>Projects</code> inside <code>Documents</code>. Don't create a SkillMatch folder yourself: the next step does that for you.</li>
<li><strong>Clone it in VS Code</strong>
<em>Cloning</em> means copying the whole shared project from GitHub onto your computer and keeping the copy linked to GitHub. In VS Code, open Source Control (<code>Ctrl+Shift+G</code>, Mac <code>Cmd+Shift+G</code>) → <strong>Clone Repository</strong> → paste this address:
<div class="cmd">https://github.com/TidyWeb/SkillMatch.git</div>
Then pick your <code>Projects</code> folder when VS Code asks where to put it. VS Code creates a folder called <code>SkillMatch</code> inside it. That folder is your clone, and the rest of these guides refer to it.</li>
<li><strong>Open it</strong>
Click <strong>Open</strong> when VS Code asks. If it asks whether you trust the authors, say yes.</li>
</ol>
<p class="done-when"><strong>Done when:</strong> the Explorer shows <code>Phil's Folder</code>, <code>Research</code> and <code>README.md</code>, and the bottom-left corner says <code>main</code>.</p>""")

page("a2-switch-on-the-ai.html", "A2", 'Pick your AI assistant',
     'Use whichever AI assistant you already like to do the typing for you. Any of them will do, as long as it can work on your SkillMatch folder. About 5 minutes.',
     """<ol class="do">
<li><strong>Choose your assistant</strong>
Use one you already know, such as Claude, Codex or Gemini, or one built into your editor. It needs to do two things: <strong>see the files in your SkillMatch folder</strong>, and <strong>run commands on your computer, asking you first</strong>. A chat window where you only copy and paste text can't do the second.</li>
<li><strong>Point it at your SkillMatch folder</strong>
Open the SkillMatch folder you cloned in <a href="a1-get-skillmatch.html">A1</a>, and start your assistant from there (or tell it to work in that folder).</li>
<li><strong>Test it</strong>
Send this, and nothing more:
<div class="cmd">Which branch is this repository on, and is anything uncommitted? Don't change anything.</div>
A good answer names a branch (probably <code>main</code>) and says whether anything is uncommitted. It should not edit a file or ask to run anything risky.</li>
</ol>
<p class="aside">No assistant that can do this? You can still do every step by hand. <a href="help.html">The help page</a> shows how to add your folder without one.</p>
<p class="done-when"><strong>Done when:</strong> your assistant has correctly told you which branch SkillMatch is on.</p>""")

A4_SCRIPT = r"""<script>
(function () {
  var template = [
    "You are helping me make my first contribution to my team's GitHub repository, TidyWeb/SkillMatch, which is open in this VS Code workspace.",
    "",
    "Goal: add a personal folder called \"{NAME}'s Folder\" at the top level of the repository, containing one file, README.md, and put it on GitHub as a pull request for Phil (GitHub user TidyWeb) to review.",
    "",
    "Rules:",
    "- Only create \"{NAME}'s Folder/README.md\". Do not change, move, rename or delete any other file.",
    "- The folder name contains an apostrophe and a space, so always put the path in double quotes in terminal commands.",
    "- Never commit to main and never force-push.",
    "- Before each step, explain in plain English what you are about to do, and wait for my approval before running any terminal command.",
    "- If anything unexpected happens (wrong repository, merge conflict, push rejected, sign-in error), stop and tell me. Do not try to fix it yourself.",
    "",
    "Steps:",
    "1. Run git remote -v and confirm the origin is https://github.com/TidyWeb/SkillMatch.git. If it isn't, stop.",
    "2. Switch to main and pull the latest changes.",
    "3. Show me the output of git config user.name and git config user.email, and ask me to confirm they are right. If either is missing, ask me for the value and set it for this repository only.",
    "4. Create and switch to a new branch called add-{SLUG}-folder.",
    "5. Ask me for two or three sentences about my background before the course and what I'd like to work on in SkillMatch. Remind me the repository is public, so nothing private. Then create \"{NAME}'s Folder/README.md\" with this content and show it to me before saving:",
    "",
    "   # {NAME}'s Folder",
    "",
    "   Working space for {NAME} in the SkillMatch hackathon project.",
    "",
    "   ## About me",
    "",
    "   (my sentences here)",
    "",
    "6. Stage only that file and commit it with the message: Add {NAME}'s folder",
    "7. Push the branch to GitHub (git push -u origin add-{SLUG}-folder).",
    "8. If you can create pull requests, open one from add-{SLUG}-folder into main titled \"Add {NAME}'s folder\". If you can't, give me the link GitHub printed after the push.",
    "9. Finish with a short summary of what you did and the pull request link."
  ].join("\n");
  var pre = document.getElementById("prompt"), copyBtn = document.getElementById("copyBtn");
  var buttons = document.querySelectorAll(".picker button");
  function fill(name) {
    pre.textContent = template.split("{NAME}").join(name).split("{SLUG}").join(name.toLowerCase());
    buttons.forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.name === name ? "true" : "false"); });
    copyBtn.textContent = "Copy prompt"; copyBtn.classList.remove("done");
  }
  buttons.forEach(function (b) { b.addEventListener("click", function () { fill(b.dataset.name); }); });
  copyBtn.addEventListener("click", function () {
    function done() { copyBtn.textContent = "Copied"; copyBtn.classList.add("done"); }
    function sel() { var r = document.createRange(); r.selectNodeContents(pre); var s = window.getSelection(); s.removeAllRanges(); s.addRange(r); copyBtn.textContent = "Selected: press Ctrl+C"; }
    if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(pre.textContent).then(done, sel); } else { sel(); }
  });
  fill("Oana");
})();
</script>"""

page("a3-add-your-folder.html", "A3", 'Add your folder',
     'One prompt, and the AI makes your folder, puts it on its own branch and uploads it. You approve each step. About 10 minutes.',
     """<ol class="do">
<li><strong>Pick your name and copy the prompt</strong>
<div aria-label="Choose your name" class="picker" role="group">
<button aria-pressed="true" data-name="Oana" type="button">Oana</button>
<button aria-pressed="false" data-name="John" type="button">John</button>
<button aria-pressed="false" data-name="Esmat" type="button">Esmat</button>
</div>
<div class="promptbox">
<button class="btn btn-lime" id="copyBtn" type="button">Copy prompt</button>
<pre aria-live="polite" id="prompt"></pre>
</div></li>
<li><strong>Paste it into your AI assistant and press Enter</strong>
It explains each step and waits for your approval before running anything. When it asks about you, remember the repository is <strong>public</strong>: background and interests, nothing private.</li>
<li><strong>Read each command before you allow it</strong>
<table class="check">
<thead><tr><th class="ok">Fine to allow</th><th class="stop">Stop and ask Phil</th></tr></thead>
<tbody>
<tr><td><code>git remote -v</code>, <code>git status</code>, <code>git config</code></td><td>Changing or deleting anything outside your folder</td></tr>
<tr><td><code>git checkout</code>, <code>git pull</code></td><td>A push with <code>--force</code> or <code>-f</code></td></tr>
<tr><td><code>git add</code>, <code>git commit</code>, <code>git push</code> on your branch</td><td>Committing while on <code>main</code>, or any "merge conflict"</td></tr>
</tbody>
</table></li>
</ol>
<p class="done-when"><strong>Done when:</strong> the AI's summary says your branch is pushed, and gives you a pull request link or a GitHub link to open one.</p>""", A4_SCRIPT)

page("a4-send-it-for-review.html", "A4", 'Send it for review',
     "Open a pull request so Phil can check your folder and add it to the shared version. Then you're a contributor. About 5 minutes.",
     """<ol class="do">
<li><strong>Open the pull request</strong>
If the AI gave you a pull request link, you're already done. If not, open <a href="https://github.com/TidyWeb/SkillMatch">github.com/TidyWeb/SkillMatch</a>, click <strong>Compare &amp; pull request</strong> on the yellow banner, check the base is <code>main</code>, and click <strong>Create pull request</strong>.</li>
<li><strong>Wait for Phil</strong>
He reviews and merges it. If he asks for a change, ask the AI to make it on the same branch and push again.</li>
<li><strong>Bring your copy up to date</strong>
In VS Code, click <code>main</code> in the bottom-left to switch back to it, then Source Control → <strong>…</strong> → <strong>Pull</strong>.</li>
</ol>
<p>Next: <a href="b1-the-big-picture.html">B1, The big picture</a>, for how branches, commits and pull requests fit together.</p>
<p class="done-when"><strong>Done when:</strong> your folder is on the <a href="https://github.com/TidyWeb/SkillMatch">repository page</a> and your picture appears under <strong>Contributors</strong>. That can take up to a day.</p>""")

page("help.html", "?", 'Stuck? Help and other routes',
     "What to do when something doesn't go to plan, and how to add your folder without an AI.",
     """<p class="callout">If something unexpected happens, stop. Don't try the fixes the AI suggests for a rejected push or a merge conflict. Take a screenshot and post it to Phil on Discord. Nothing you do on your own branch can break the shared version.</p>
<h2>No AI? Use the browser</h2>
<ol class="do">
<li><strong>Create the file</strong>
On <a href="https://github.com/TidyWeb/SkillMatch">github.com/TidyWeb/SkillMatch</a>: <strong>Add file → Create new file</strong>. Name it <code>Esmat's Folder/README.md</code>, using your own name. Typing the <code>/</code> makes the folder.</li>
<li><strong>Write two or three public-safe sentences about yourself</strong></li>
<li><strong>Propose it</strong>
<strong>Commit changes…</strong> → <strong>Create a new branch for this commit and start a pull request</strong> → <strong>Propose changes</strong> → <strong>Create pull request</strong>.</li>
</ol>
<h2>Not showing as a contributor?</h2>
<p>GitHub credits a commit to you only if its email belongs to your GitHub account. Check GitHub → Settings → Emails and tell Phil if they don't match.</p>""")

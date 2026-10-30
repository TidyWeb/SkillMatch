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

page("b1-the-big-picture.html", "B1", 'The big picture',
     "GitHub's words make more sense next to something you may already know: a shared document in Microsoft Word with its Track Changes feature switched on. Read this once, and the rest of the guides will feel like steps you already understand.",
     """<h2>First, Microsoft Word's Track Changes</h2>
<p>Microsoft Word, the word processor, has a feature called <strong>Track Changes</strong> (on the Review tab). When it's switched on, Word no longer quietly overwrites the text. Every edit you make is <em>marked</em>: deleted words are struck through, new words are underlined, and each mark carries your name. Someone else can then read through your marked edits, leave <strong>comments</strong> in the margin, and <strong>accept</strong> or <strong>reject</strong> each change. Clicking <strong>Accept All Changes</strong> folds them into the finished document.</p>
<p>You don't need to have used it. The point is the habit it builds: you edit, someone checks, and only then does your edit become part of the document everyone relies on.</p>
<h2>Now picture the team using it</h2>
<p>Four people are writing one Microsoft Word document. Everyone needs to edit it, but nobody should be able to wreck it, and nobody wants to wait their turn. So each person works on their <em>own copy</em> with Track Changes on, hands it to a teammate to check, and only the accepted changes go into the master copy. GitHub works the same way. It just uses different names for each part, and the table below matches them up.</p>
<table>
<thead><tr><th>GitHub says</th><th>In Microsoft Word terms</th><th>What you actually do</th></tr></thead>
<tbody>
<tr><td><strong>main</strong></td><td>The agreed master document</td><td>Never edit it directly. You read it and copy from it.</td></tr>
<tr><td><strong>Branch</strong></td><td>Your own copy of the master</td><td>Make one per task, named after your card.</td></tr>
<tr><td><strong>Commit</strong></td><td>Saving your copy at a good moment</td><td>Stage the files, write a one-line message, click Commit.</td></tr>
<tr><td><strong>Push</strong></td><td>Handing your copy over</td><td>Publish Branch the first time, Sync Changes after that.</td></tr>
<tr><td><strong>Pull request</strong></td><td>"Please pull my changes in"</td><td>Open it on GitHub and choose a reviewer.</td></tr>
<tr><td><strong>Review</strong></td><td>Comments in the margin</td><td>A teammate reads your changes, then approves or asks for fixes.</td></tr>
<tr><td><strong>Merge</strong></td><td>"Accept all changes"</td><td>Phil clicks it, for now. Your work is now part of main.</td></tr>
<tr><td><strong>Squash</strong></td><td>All your edits become one tidy entry</td><td>Nothing to do. GitHub does it when merging.</td></tr>
</tbody>
</table>
<div aria-label="Five stages in a change" class="flow">
<div class="box"><b>1 · Branch</b>Your own copy to edit.<span class="who">You</span></div>
<div class="box"><b>2 · Commit</b>Save a checkpoint.<span class="who">You</span></div>
<div class="box"><b>3 · Push</b>Send the branch to GitHub.<span class="who">You</span></div>
<div class="box shared"><b>4 · Pull request + review</b>Ask for the changes to be accepted; a teammate checks them.<span class="who">You ask; a teammate reviews</span></div>
<div class="box shared"><b>5 · Merge</b>Accepted into main.<span class="who">Phil, for now</span></div>
</div>
<h2>"Pull" means two different things</h2>
<table>
<thead><tr><th>You see</th><th>It means</th><th>Which way it goes</th></tr></thead>
<tbody>
<tr><td><strong>Pull</strong> (Source Control → Pull)</td><td>Download the latest shared version onto your computer.</td><td>GitHub → you</td></tr>
<tr><td><strong>Pull request</strong></td><td>Ask the team to accept your changes into main.</td><td>You → main</td></tr>
</tbody>
</table>
<p>If a guide says "pull", it means the first. If it says "pull request", it means the second. GitLab calls a pull request a "merge request". Same thing.</p>
<h2>One change, start to finish</h2>
<p>Here is the whole route with a real task: Oana has a card to collect interface screenshots.</p>
<ol class="do">
<li><strong>She starts from the latest main</strong>
So her copy matches what the team has agreed so far (<a href="d1-start-from-the-latest.html">D1</a>).</li>
<li><strong>She makes a branch</strong>
Named after her card, so everyone can see what it's for (<a href="d2-make-a-branch.html">D2</a>).</li>
<li><strong>She adds her files and commits</strong>
Checkpoints she can come back to (<a href="b3-add-files-to-the-repository.html">B3</a>).</li>
<li><strong>She pushes and opens a pull request</strong>
Her branch is now on GitHub, and she asks Phil to review it (<a href="b4-open-a-pull-request-properly.html">B4</a>).</li>
<li><strong>Phil reviews and merges</strong>
Her work is now in main. Everyone else's next "pull" brings it down to their computer (<a href="e1-review-a-pull-request.html">E1</a>, <a href="e2-merge-it.html">E2</a>).</li>
</ol>
<h2>Why it works this way</h2>
<p>Every change is seen by a second person before it becomes part of the shared version, and every mistake is confined to someone's own branch. Main is protected, so nobody can push to it directly, Phil included. That sounds like extra work. For a new team, it catches a slip before it affects the shared project.</p>
<p class="done-when"><strong>Done when:</strong> you can say the five stages in order (branch, commit, push, pull request and review, merge) and explain the two meanings of "pull".</p>""")

page("b2-your-copy-and-the-shared-copy.html", "B2", 'Your copy and the shared copy',
     "A file can be on GitHub, in your linked clone folder, or somewhere else on your computer. Knowing which one you're looking at explains almost every “why isn't my file on GitHub?” moment.",
     """<p class="aside"><strong>Before this guide:</strong> you've done <a href="a1-get-skillmatch.html">A1</a>, so SkillMatch is already cloned on your computer. This guide explains what that gave you.</p>
<figure aria-label="Three places a file can be, and how they connect" class="stack">
<div class="place"><strong>1 · GitHub</strong><span>The shared repository, online. Everyone's work ends up here. Also called <em>origin</em>.</span></div>
<div class="link"><span>↓ clone (once), then pull</span><span>↑ push</span></div>
<div class="place"><strong>2 · Your clone folder</strong><span>A folder on your computer that is linked to GitHub. This is the folder VS Code has open.</span></div>
<div class="link manual"><span>↕ you copy files in by hand</span></div>
<div class="place outside"><strong>3 · Everywhere else on your computer</strong><span>Downloads, Documents, course folders. GitHub knows nothing about these.</span></div>
<figcaption>Only the clone folder is linked. A file in place 3 has to be copied into place 2 before Git can see it, and committed and pushed before GitHub can.</figcaption>
</figure>
<h2>Find out where your clone is</h2>
<ol class="do">
<li><strong>Open the clone in VS Code</strong>
<strong>File → Open Recent</strong> → SkillMatch. The Explorer on the left now shows the clone's contents.</li>
<li><strong>Reveal it on your computer</strong>
Right-click any file in the Explorer → <strong>Reveal in File Explorer</strong> (Windows), <strong>Reveal in Finder</strong> (Mac) or <strong>Open Containing Folder</strong> (Linux). The window that opens is your clone. Remember where it is.</li>
<li><strong>Read the bottom-left corner</strong>
It shows the branch you're on, such as <code>main</code>. Every guide that says "check the bottom-left" means this.</li>
</ol>
<h2>Prove it to yourself (2 minutes)</h2>
<p>This test shows what GitHub can and can't see. It changes nothing on GitHub, as long as you do the last step.</p>
<ol class="do">
<li><strong>Make a file outside the clone</strong>
In your Downloads folder, create a text file called <code>test.txt</code>. Look at VS Code's Source Control. Nothing appears, because VS Code and Git don't know the file exists.</li>
<li><strong>Move it into the clone</strong>
Drag <code>test.txt</code> into the clone folder you revealed above. Source Control now lists <code>test.txt</code> with a <code>U</code> beside it. <code>U</code> means untracked: Git can see the file but isn't keeping track of it yet.</li>
<li><strong>Delete it</strong>
Delete <code>test.txt</code> from the clone folder. Source Control goes quiet again. Don't commit it.</li>
</ol>
<h2>Where is my change right now?</h2>
<p>"It's not on GitHub!" almost always means the change hasn't reached that step yet. Each action moves it one place further.</p>
<table>
<thead><tr><th>You have…</th><th>Your change is…</th><th>Who can see it</th></tr></thead>
<tbody>
<tr><td>Saved the file</td><td>In your clone folder, not yet committed</td><td>Only you</td></tr>
<tr><td>Committed it</td><td>A checkpoint on your branch, still on your computer</td><td>Only you</td></tr>
<tr><td>Pushed (Publish Branch / Sync Changes)</td><td>On GitHub, on your branch</td><td>Anyone who opens the repository, but it isn't in main yet</td></tr>
<tr><td>Had the pull request merged</td><td>In main on GitHub</td><td>Everyone, once they pull</td></tr>
<tr><td>Pulled (a teammate does this)</td><td>In their clone folder too</td><td>Them</td></tr>
</tbody>
</table>
<h2>Two words you'll keep seeing</h2>
<p><strong>origin</strong> is the short name your clone uses for the GitHub repository it came from. <strong>main</strong> is the team's agreed shared branch. That's all either word means.</p>
<p class="callout">If a file isn't inside the clone folder, GitHub can't see it. If it's in the clone but you haven't committed and pushed it, only you can see it.</p>
<p class="done-when"><strong>Done when:</strong> you can point to your clone folder, and explain why a screenshot sitting in Downloads isn't on GitHub.</p>""")

page("b3-add-files-to-the-repository.html", "B3", 'Add files to the repository',
     'A worked example from start to finish: collect interface screenshots, put them in your own folder with a note about each, and send them for review. The same steps work for any file you add.',
     """<section aria-label="Before you start" class="keypoints"><h2>Before you start</h2>
<ul>
<li>You've done <a href="a1-get-skillmatch.html">A1</a> (SkillMatch is cloned) and <a href="a3-add-your-folder.html">A3</a> (your own folder exists in the repository).</li>
<li>Collect your screenshots somewhere <strong>outside</strong> the clone first, such as a folder called <code>ui-examples-draft</code> in Documents. Decide which ones are allowed in (see the warnings below), and only then copy those in.</li>
<li>You have your card's number from the <a href="https://github.com/users/TidyWeb/projects/3">project board</a>.</li>
</ul></section>
<h2>Step by step</h2>
<ol class="do">
<li><strong>Start from the latest</strong>
Follow <a href="d1-start-from-the-latest.html">D1</a>, so your clone matches the team's current main. <em>You should see:</em> <code>main</code> in the bottom-left, and Pull reporting nothing new.</li>
<li><strong>Make a branch for your card</strong>
Follow <a href="d2-make-a-branch.html">D2</a>. <em>You should see:</em> your new branch name in the bottom-left, not <code>main</code>.</li>
<li><strong>Make the folder for the examples</strong>
In the VS Code Explorer, right-click your own folder (for example <code>Oana's Folder</code>) → <strong>New Folder</strong> → type <code>ui-examples</code>. <em>You should see:</em> the new folder inside yours. (An empty folder won't appear in Source Control yet. Git only tracks files.)</li>
<li><strong>Put the images in</strong>
Drag your chosen PNG or JPG files from your file manager into <code>ui-examples</code> in the Explorer. You can also copy them in with the file manager, into that same folder inside the clone. <em>You should see:</em> the images listed under <code>ui-examples</code>.</li>
<li><strong>Name each image clearly</strong>
Lowercase, hyphens between words, no spaces (brief rule 4.8). Right-click a file → <strong>Rename</strong>. Name it after what it shows:
<div class="cmd">airbnb-search-results.png
duolingo-lesson-complete.png
monzo-spending-summary.jpg</div></li>
<li><strong>Keep each image small</strong>
Aim for under about 1 MB each. That's our own rule, so the repository stays quick for everyone to download. It isn't a GitHub limit. Most screenshots need no change. If one is big, shrink it in any image editor (Paint on Windows: <strong>Resize</strong>; Preview on Mac: <strong>Tools → Adjust Size</strong>) and save it again.</li>
<li><strong>Write a note for each one in links.md</strong>
Create a file called <code>links.md</code> inside <code>ui-examples</code>. One line per example: the file name, where it came from, and why it's worth looking at:
<div class="cmd">airbnb-search-results.png | https://www.airbnb.co.uk/ | Filters stay visible while you scroll the results.
duolingo-lesson-complete.png | https://www.duolingo.com/ | Small celebration at the end of a task; could suit "profile complete".</div>
If you decide <em>not</em> to upload an image, still add its line, with the URL, and leave the image out.</li>
<li><strong>Check what Git can see</strong>
Open Source Control (<code>Ctrl+Shift+G</code>, Mac <code>Cmd+Shift+G</code>). Under <strong>Changes</strong> you should see each new file with a <code>U</code> beside it. <code>U</code> means untracked: new, not yet saved into a commit. <em>Nothing showing?</em> The files are outside the clone folder. Go back to <a href="b2-your-copy-and-the-shared-copy.html">B2</a>.</li>
<li><strong>Stage, then commit</strong>
Click <strong>+</strong> beside only the files for this task. They move up to <strong>Staged Changes</strong>. Type a plain message in the box, for example <code>Add interface screenshot examples</code>, and click <strong>Commit</strong>.</li>
<li><strong>Publish the branch</strong>
Click <strong>Publish Branch</strong> (the first time). After that, <strong>Sync Changes</strong>. <em>You should see:</em> the button disappears, and your branch is now on GitHub.</li>
<li><strong>Open a pull request</strong>
Follow <a href="b4-open-a-pull-request-properly.html">B4</a>. In the description, say which card this is for, and check the number (<a href="b5-cards-and-closes.html">B5</a>).</li>
<li><strong>Check it after it's merged</strong>
Open <a href="https://github.com/TidyWeb/SkillMatch">github.com/TidyWeb/SkillMatch</a>, then your folder, then <code>ui-examples</code>. Your files and <code>links.md</code> should be there.</li>
</ol>
<p class="callout"><strong>Check you're allowed to upload each image.</strong> The repository is <strong>public</strong>: anyone on the internet can see it. Most example screenshots belong to other companies, or to the people who posted them on Mobbin or Refero. Upload an image only if its licence allows it. If you can't tell, put the URL and your note in <code>links.md</code> and leave the image out. A link is always safe to share.</p>
<p class="callout"><strong>Keep private information out.</strong> Never upload anything showing an API key, a password, an email address or personal data. Look at each screenshot before you copy it in, including the corners and the browser bar. Do not add folders you didn't create for this task.</p>
<h2>If something goes wrong</h2>
<table>
<thead><tr><th>You see</th><th>It usually means</th><th>Do this</th></tr></thead>
<tbody>
<tr><td>Source Control shows nothing</td><td>The files are outside the clone folder</td><td>Move or copy them into <code>ui-examples</code> in the Explorer</td></tr>
<tr><td>The branch name says <code>main</code></td><td>You skipped D2</td><td>Make the branch now; your changes come with you. Do not commit on main</td></tr>
<tr><td>Push is rejected</td><td>You committed on main, or the branch isn't published</td><td>Check the bottom-left. If it says main, ask Phil before doing anything else</td></tr>
<tr><td>You staged a file by mistake</td><td>Easy to undo</td><td>Click <strong>−</strong> beside it in Staged Changes to unstage it</td></tr>
<tr><td>A screenshot shows something private</td><td>Not committed yet: fine</td><td>Delete it from the folder. If it's already pushed, tell Phil straight away</td></tr>
</tbody>
</table>
<p class="aside"><strong>Prefer your AI assistant to do it?</strong> Paste this into whichever one you use, and check what it proposes before allowing anything:</p>
<div class="cmd">In this repository, add interface screenshot examples to my existing personal folder. First show me the current branch and which files would change. Create only a ui-examples folder inside my folder, the image files I provide, and a links.md with one line per image giving its source URL and why it's interesting. The folder name contains an apostrophe and a space, so always put paths in double quotes in terminal commands. Do not add an image unless I confirm its licence allows public reuse. Do not include keys, passwords, email addresses or personal data. Use lowercase, hyphenated image names. Work on a new branch, never on main. Stage only these files, show me the staged list, and wait for my approval before committing or pushing. Never force-push.</div>
<p class="done-when"><strong>Done when:</strong> the pull request is merged, your files appear in your folder on GitHub, and every image you uploaded is one you're allowed to share, with a note in <code>links.md</code>.</p>""")

page("b4-open-a-pull-request-properly.html", "B4", 'Open a pull request, properly',
     'A pull request asks the team to check your branch before it joins the shared version. This guide covers the form, every box on its right-hand side, and what happens after you click Create.',
     """<ol class="do">
<li><strong>Start it</strong>
After you've published your branch, open <a href="https://github.com/TidyWeb/SkillMatch">the repository</a>. A yellow banner offers <strong>Compare &amp; pull request</strong>. Click it. (No banner? <strong>Pull requests → New pull request</strong>, and choose your branch.)</li>
<li><strong>Check the direction</strong>
At the top it should read <code>base: main ← compare: your-branch</code>. That means: "take the changes on my branch and propose them for main". If the two are the wrong way round, fix them before going on.</li>
<li><strong>Write the title</strong>
Say what the change does, in plain words: <code>Add vacancy source research notes</code>.</li>
<li><strong>Write the description</strong>
Two or three lines: what you changed, why, and which card it belongs to. For example:
<div class="cmd">Adds my notes on two vacancy sources and their URLs for the source library.

Closes #31</div>
The last line connects the pull request to a card. <strong>The number here is an example. Use your own card's number.</strong> <a href="b5-cards-and-closes.html">B5</a> explains it, and how to get it right.</li>
<li><strong>Go through the sidebar, top to bottom</strong>
The column on the right has several boxes. The table below says which ones matter.</li>
<li><strong>Read it once more, then create it</strong>
Base, branch, reviewer, assignee, the Development box. Then <strong>Create pull request</strong>.</li>
</ol>
<h2>The sidebar, box by box</h2>
<table>
<thead><tr><th>Box</th><th>What it's for</th><th>Do you need it?</th></tr></thead>
<tbody>
<tr><td><strong>Reviewers</strong></td><td>Who should check it. You can't review your own.</td><td><strong>Yes, always.</strong> Choose Phil, or whoever the team has agreed.</td></tr>
<tr><td><strong>Assignees</strong></td><td>Who is responsible for it.</td><td><strong>Yes: assign yourself</strong> (click "assign yourself").</td></tr>
<tr><td><strong>Labels</strong></td><td>Tags for sorting.</td><td>No. Labels live on the card, not the pull request.</td></tr>
<tr><td><strong>Projects</strong></td><td>Puts it on a project board.</td><td>No. The card is already on the board.</td></tr>
<tr><td><strong>Milestone</strong></td><td>Groups work by target.</td><td>No. The card carries it.</td></tr>
<tr><td><strong>Development</strong></td><td>Which card this pull request will close when it's merged.</td><td><strong>Check it.</strong> It should say "None yet" unless this pull request finishes a card.</td></tr>
</tbody>
</table>
<section aria-label="Assignees" class="keypoints"><h2>"Do I have to assign myself?"</h2>
<p>No. Nothing breaks if you don't. But the board's <strong>Team items</strong> view groups work by person, so a pull request with no assignee appears under nobody, and nobody can see whose it is. It costs one click, so do it.</p></section>
<h2>After you click Create</h2>
<ol class="do">
<li><strong>Your reviewer is notified</strong>
They'll read the <strong>Files changed</strong> tab and either approve, comment, or ask for changes.</li>
<li><strong>If they comment or ask for changes</strong>
Fix things on the <em>same branch</em>, commit and Sync. The pull request updates itself. You don't open a new one (<a href="d5-after-its-merged.html">D5</a>).</li>
<li><strong>When it's merged</strong>
The top of the page turns purple and says <strong>Merged</strong>. Your branch is deleted for you. Now pull main (<a href="d1-start-from-the-latest.html">D1</a>) and start your next card.</li>
</ol>
<p class="done-when"><strong>Done when:</strong> the pull request is open with the right base and branch, a reviewer, you as assignee, and a Development box that says what you meant it to.</p>""")

page("b5-cards-and-closes.html", "B5", "Cards, numbers and 'Closes'",
     'Every card on the project board is a numbered GitHub issue. One short line in a pull request connects the two, and can close the card automatically when the change is merged. Get the number wrong and it closes the wrong card.',
     """<h2>Where the number comes from</h2>
<ol class="do">
<li><strong>Open the board</strong>
<a href="https://github.com/users/TidyWeb/projects/3">The SkillMatch project board</a>. Every card is a GitHub <em>issue</em>.</li>
<li><strong>Click a card</strong>
Its number is next to the title, with a hash: <code>#27</code>. It's also at the end of the address in your browser.</li>
</ol>
<p class="callout"><strong>Apart from card 27 in the warning further down, the card numbers in these examples are made up.</strong> Never copy one. Use the number of your own card, or you may close someone else's.</p>
<h2>What "Closes #27" does</h2>
<p>If the description of a pull request has this on a line of its own:</p>
<div class="cmd">Closes #27</div>
<p>then when the pull request is <strong>merged</strong>, GitHub closes issue 27 automatically, and the card moves to Done on the board. Nobody has to drag anything. <code>Fixes #27</code> and <code>Resolves #27</code> do the same thing. This only happens when the pull request goes into main.</p>
<div aria-label="From pull request to a finished card" class="flow">
<div class="box"><b>1 · The card</b>"Add interface examples", card <code>#31</code> on the board.<span class="who">Find its number</span></div>
<div class="box"><b>2 · The description</b>Your pull request ends with <code>Closes #31</code>.<span class="who">You write it</span></div>
<div class="box shared"><b>3 · Merge</b>The pull request is accepted into main.<span class="who">After review</span></div>
<div class="box"><b>4 · Card finished</b>Issue 31 closes; the card moves to Done.<span class="who">Automatic</span></div>
</div>
<h2>The three things you can write</h2>
<table>
<thead><tr><th>You write</th><th>What happens on merge</th><th>Use it when</th></tr></thead>
<tbody>
<tr><td><code>Closes #31</code></td><td>Card 31 closes and moves to Done</td><td>This pull request <em>finishes</em> the card</td></tr>
<tr><td><code>Supports #31</code></td><td>Card 31 gets a link to this pull request, and stays open</td><td>It's part of the card's work, but not all of it</td></tr>
<tr><td><code>Closes: none</code></td><td>Nothing closes</td><td>It belongs to no card. This one is our own convention</td></tr>
</tbody>
</table>
<p>Two cards at once: repeat the word, <code>Closes #31, closes #32</code>. A single <code>Closes #31, #32</code> only closes the first.</p>
<h2>Why the number matters</h2>
<p class="callout">A real example from this project: an AI assistant guessed <code>Closes #27</code>. Card 27 was "Agree how we work", the team's first planning card. If that pull request had been merged, the card would have closed itself, with the team's first job not done.</p>
<h2>Check before you create</h2>
<ol class="do">
<li><strong>Read the card's title next to its number</strong>
Does card 31 really say what this pull request does?</li>
<li><strong>Look at the Development box</strong>
On the pull request form, the sidebar's <strong>Development</strong> box lists which card will close. "None yet" is right unless you meant to close one.</li>
<li><strong>Not sure? Write <code>Closes: none</code></strong>
It's always safe. Phil can link the card when he reviews.</li>
</ol>
<h2>If it's wrong</h2>
<p><strong>Before it's merged:</strong> edit the description (the pencil on the pull request's first comment) and correct the line. <strong>After:</strong> open the card that closed and click <strong>Reopen</strong>, then tell Phil.</p>
<p>GitHub's own explanation: <a href="https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue">Linking a pull request to an issue</a>.</p>
<p class="done-when"><strong>Done when:</strong> you can find a card's number, say what <code>Closes #31</code> will do, and check the Development box before creating a pull request.</p>""")

page("b6-glossary.html", "B6", 'Glossary',
     'Every GitHub and VS Code word used in these guides, in plain English, each with a link to where you actually do it.',
     """<dl class="gloss">
<dt>API key</dt><dd>A private password that lets an app use a service. Never put one in the repository, a screenshot or a chat.</dd>
<dt>Assignee</dt><dd>The person responsible for a pull request or card. On your own pull request, assign yourself. <a href="b4-open-a-pull-request-properly.html">B4</a></dd>
<dt>Base / compare</dt><dd>The two ends of a pull request: <em>base</em> is where the changes are going (main), <em>compare</em> is your branch. <a href="b4-open-a-pull-request-properly.html">B4</a></dd>
<dt>Branch</dt><dd>Your own copy of the project to work in, separate from main. One per card. <a href="d2-make-a-branch.html">D2</a></dd>
<dt>Card</dt><dd>One task on the project board. Each card is a numbered GitHub issue. <a href="b5-cards-and-closes.html">B5</a></dd>
<dt>Clone</dt><dd>A copy of the repository on your computer that stays linked to GitHub. <a href="a1-get-skillmatch.html">A1</a>, <a href="b2-your-copy-and-the-shared-copy.html">B2</a></dd>
<dt>Clone folder</dt><dd>The folder on your computer that the clone lives in. Only files inside it can be shared through Git. <a href="b2-your-copy-and-the-shared-copy.html">B2</a></dd>
<dt>Closes #n</dt><dd>A line in a pull request description that closes card n when the pull request is merged. <a href="b5-cards-and-closes.html">B5</a></dd>
<dt>Commit</dt><dd>A saved checkpoint of your changes on your branch. <a href="d3-save-and-upload.html">D3</a></dd>
<dt>Commit message</dt><dd>The one line you write with a commit, saying what changed. <a href="d3-save-and-upload.html">D3</a></dd>
<dt>Conflict</dt><dd>Two people changed the same lines, so GitHub can't choose between them. Someone decides. <a href="e3-when-theres-a-conflict.html">E3</a></dd>
<dt>Development (box)</dt><dd>The sidebar box on a pull request that shows which card it will close. Check it before you create the pull request. <a href="b4-open-a-pull-request-properly.html">B4</a>, <a href="b5-cards-and-closes.html">B5</a></dd>
<dt>Explorer</dt><dd>The file list on the left of VS Code. <a href="b2-your-copy-and-the-shared-copy.html">B2</a></dd>
<dt>Issue</dt><dd>GitHub's word for a numbered task or discussion. Our board cards are issues. <a href="b5-cards-and-closes.html">B5</a></dd>
<dt>Label</dt><dd>A coloured tag for sorting cards. Set on the card, not the pull request. <a href="b4-open-a-pull-request-properly.html">B4</a></dd>
<dt>main</dt><dd>The team's agreed, shared version. Nobody edits it directly; changes arrive through pull requests. <a href="b1-the-big-picture.html">B1</a></dd>
<dt>Merge</dt><dd>Accept a reviewed pull request into main. <a href="e2-merge-it.html">E2</a></dd>
<dt>Milestone</dt><dd>A group of cards with a shared target. Set on the card. <a href="b4-open-a-pull-request-properly.html">B4</a></dd>
<dt>origin</dt><dd>The short name your clone uses for the GitHub repository it came from. <a href="b2-your-copy-and-the-shared-copy.html">B2</a></dd>
<dt>Protect main</dt><dd>The rule that stops anyone pushing straight to main. <a href="e4-protect-main.html">E4</a></dd>
<dt>Publish Branch</dt><dd>The VS Code button that sends a new branch to GitHub for the first time. After that it's Sync Changes. <a href="d3-save-and-upload.html">D3</a></dd>
<dt>Pull</dt><dd>Download the latest shared version onto your computer. Not the same as a pull request. <a href="d1-start-from-the-latest.html">D1</a></dd>
<dt>Pull request</dt><dd>A request for the team to check your branch and accept its changes into main. <a href="b4-open-a-pull-request-properly.html">B4</a></dd>
<dt>Push</dt><dd>Send your committed changes from your computer to GitHub. <a href="d3-save-and-upload.html">D3</a></dd>
<dt>Repository (repo)</dt><dd>The project's files plus their whole history, kept on GitHub and in each clone. <a href="b2-your-copy-and-the-shared-copy.html">B2</a></dd>
<dt>Review</dt><dd>Reading someone's pull request, then approving it or asking for changes. <a href="e1-review-a-pull-request.html">E1</a></dd>
<dt>Squash</dt><dd>Merging all of a pull request's commits as one tidy entry. <a href="e2-merge-it.html">E2</a></dd>
<dt>Stage</dt><dd>Choose which changed files go into the next commit (the <strong>+</strong> beside a file). <a href="b3-add-files-to-the-repository.html">B3</a></dd>
<dt>Source Control</dt><dd>The VS Code panel for staging, committing and syncing. <code>Ctrl+Shift+G</code>, Mac <code>Cmd+Shift+G</code>. <a href="d3-save-and-upload.html">D3</a></dd>
<dt>Status bar</dt><dd>The strip along the bottom of VS Code. Its left end shows your branch. <a href="b2-your-copy-and-the-shared-copy.html">B2</a></dd>
<dt>Sync Changes</dt><dd>The VS Code button that sends your new commits to GitHub (and brings down any from the same branch). <a href="d3-save-and-upload.html">D3</a></dd>
<dt>Untracked (U)</dt><dd>A new file Git can see but isn't recording yet. Stage it to include it. <a href="b3-add-files-to-the-repository.html">B3</a></dd>
</dl>
<p class="done-when"><strong>Done when:</strong> you can find a word you don't know, and follow its link to the guide where you do it.</p>""")



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

page("e1-review-a-pull-request.html", "E1", 'Review a pull request',
     "Read someone's proposed change, comment on it, and either approve it or ask for changes. You can't review your own.",
     """<ol class="do">
<li><strong>Open it</strong>
Repository → <strong>Pull requests</strong> → click the one you've been asked to review.</li>
<li><strong>Read the changes</strong>
<strong>Files changed</strong> tab. To comment on a line, hover over it and click <strong>+</strong>.</li>
<li><strong>Give your verdict</strong>
<strong>Review changes</strong> (top right) → <strong>Comment</strong>, <strong>Approve</strong> or <strong>Request changes</strong> → <strong>Submit review</strong>.</li>
</ol>
<table class="check">
<thead><tr><th class="ok">Check that</th><th class="stop">Request changes if</th></tr></thead>
<tbody>
<tr><td>It does what its card says</td><td>It changes files it has no reason to touch</td></tr>
<tr><td>File names have no spaces or capitals (brief rule 4.8)</td><td>It contains a key, password, or real advert data</td></tr>
<tr><td>Anything visual has been checked on the live page</td><td>You can't tell what it does from the description</td></tr>
</tbody>
</table>
<p class="done-when"><strong>Done when:</strong> your review is submitted and shows on the pull request.</p>""")

page("e2-merge-it.html", "E2", 'Merge it',
     'Add an approved pull request to the shared version. Phil is the only person who merges.',
     """<ol class="do">
<li><strong>Check it's ready</strong>
On the <strong>Conversation</strong> tab: every comment resolved, and no message saying the branch has conflicts (if it has, see <a href="e3-when-theres-a-conflict.html">E3</a>).</li>
<li><strong>Squash and merge</strong>
Click <strong>Squash and merge</strong>, tidy the message so it says what changed, then <strong>Confirm squash and merge</strong>. The whole pull request becomes one clean commit on <code>main</code>.</li>
<li><strong>Let GitHub tidy up</strong>
The branch is deleted automatically, and any card named with <code>Closes #n</code> moves to Done.</li>
</ol>
<p class="done-when"><strong>Done when:</strong> the pull request says <strong>Merged</strong>. For pages on the hub, check the live page a couple of minutes later.</p>""")

page("e3-when-theres-a-conflict.html", "E3", "When there's a conflict",
     "A conflict means two people changed the same lines. GitHub won't guess which version to keep, so someone has to choose.",
     """<ol class="do">
<li><strong>Spot it</strong>
The pull request says <strong>This branch has conflicts that must be resolved</strong>.</li>
<li><strong>Small text clash: fix it on GitHub</strong>
Click <strong>Resolve conflicts</strong>. Each clash is shown between markers:
<div class="cmd">&lt;&lt;&lt;&lt;&lt;&lt;&lt; your branch
your version
=======
the version already on main
&gt;&gt;&gt;&gt;&gt;&gt;&gt; main</div>
Keep the right lines, delete all three marker lines, then <strong>Mark as resolved → Commit merge</strong>.</li>
<li><strong>Code, or not sure: send it back</strong>
Comment on the pull request asking the author to update their branch, or ask Phil. Don't guess with code.</li>
</ol>
<p class="callout">Never force-push to get past a conflict, and never delete or rename main. The protection on main blocks both anyway.</p>
<p class="done-when"><strong>Done when:</strong> the conflict message has gone and the pull request can be merged (E2).</p>""")

page("e4-protect-main.html", "E4", 'Protect main',
     'Why nobody can push straight to the shared version, and how the rule is set. For the repository owner.',
     """<section aria-label="What's set" class="keypoints"><h2>The rule on main (ruleset "Protect main")</h2>
<ul>
<li><strong>Pull request required:</strong> every change goes through a pull request, Phil's included. No exceptions.</li>
<li><strong>Approvals needed: 0 for now,</strong> so work isn't stuck waiting while people are busy. It can be raised to 1 for the hackathon week.</li>
<li><strong>Squash merges only;</strong> <strong>no force pushes;</strong> <strong>main can't be deleted.</strong></li>
<li><strong>Merged branches delete themselves.</strong></li>
</ul></section>
<ol class="do">
<li><strong>See it</strong>
Repository → <strong>Settings → Rules → Rulesets → Protect main</strong>.</li>
<li><strong>Require a reviewer (when the team agrees)</strong>
Under <strong>Require a pull request before merging</strong>, set <strong>Required approvals</strong> to 1 → <strong>Save changes</strong>.</li>
</ol>
<p class="done-when"><strong>Done when:</strong> a direct push to main is rejected, and changes arrive only through merged pull requests.</p>""")
page("c3-how-skillmatch-finds-the-jobs.html", "C3", 'How SkillMatch finds the jobs', "SkillMatch doesn't make up vacancies. Each night it visits a list of websites, saves what is advertised there, drops the adverts a Code Institute graduate shouldn't see, and links every advert that's left back to the page it came from. This guide walks through each stage and lists every website on the list.",
     """<p class="callout"><strong>Where this stands on 26 October 2026.</strong> Working now: Reed, four employer job boards (Gymshark, Monzo, Kpler and Biffa), We Work Remotely and Remote OK. Not built yet: reading the recruitment agencies' own pages, which is most of the list at the bottom. Waiting: CV-Library's jobs feed, requested through their website on 22 October.</p>
<h2>The idea, in a shop window</h2>
<p>Picture someone walking round every recruitment agency in the West Midlands, photographing the adverts in the windows. Back at a desk, they sort the photos. Senior roles go in the bin. So do jobs in Newcastle, and courses dressed up as jobs. Whatever is left gets pinned to a board, each with a note saying which window it came from. A graduate looking at that board sees only adverts worth their time, and one click takes them back to the real advert to apply.</p>
<p>SkillMatch does the same thing with a computer, and does it every night. The five stages are below.</p>
<div aria-label="Five stages from website to results page" class="flow">
<div class="box"><b>1 · Choose the websites</b>A list of web addresses.<span class="who">Phil's register</span></div>
<div class="box"><b>2 · Fetch the pages</b>Ask each site for its page of adverts.<span class="who">The computer</span></div>
<div class="box"><b>3 · Pull out the details</b>Title, employer, town, salary, link.<span class="who">The computer</span></div>
<div class="box shared"><b>4 · Filter</b>Drop what a graduate shouldn't see.<span class="who">Rules we wrote</span></div>
<div class="box shared"><b>5 · Match and link back</b>Score the fit, send the click to the original.<span class="who">SkillMatch</span></div>
</div>
<h2>Step by step</h2>
<ol class="do">
<li><strong>Choose the websites</strong>
Every site SkillMatch reads is on one list, called the source register. It lives in <code>Research/Vacancy_Sources/source_register.json</code> and has 96 entries. Each entry records the site's name, its address (a URL, the text you type into a browser's address bar), what kind of site it is, and which area it covers. Nothing gets visited unless it is on this list. The whole list is at the bottom of this page.</li>
<li><strong>Fetch the page</strong>
The computer asks the site for a page, the same way your browser does. What comes back is HTML, the code that describes the page. Headings, lists and links are each wrapped in labels called tags. For a recruiter's search page, the result is a list of perhaps twenty adverts. The computer waits about a second between requests. The app keeps recent responses in a temporary on-disk cache for up to 20 hours, so repeat runs can reuse them instead of asking for the same page again straight away. Going slowly helps prevent a site from blocking us.</li>
<li><strong>Find the adverts in the code</strong>
On any one site, every advert in a list is built the same way. Open the page's code and you can see the pattern: a box, a title inside it, a company name, a town, a link. For each site we write a short recipe saying where those pieces sit. Programmers call that recipe a selector. Here is a made-up example of what the code for one advert might look like.
<div class="cmd code">&lt;div class="job-card"&gt;
  &lt;h3&gt;&lt;a href="/jobs/4471"&gt;Junior Data Analyst&lt;/a&gt;&lt;/h3&gt;
  &lt;span class="company"&gt;Example Recruitment&lt;/span&gt;
  &lt;span class="town"&gt;Coventry&lt;/span&gt;
  &lt;span class="pay"&gt;£26,000 - £30,000&lt;/span&gt;
&lt;/div&gt;</div>
The recipe for this site would say: the title is the link inside the <code>h3</code>, the town is the <code>span</code> marked <code>town</code>, and so on. Every site needs its own recipe. That is the main cost of this approach.</li>
<li><strong>Put every advert into the same shape</strong>
Sites name things differently. One says "Location", another says "Where", another puts the town in the title. So each advert is rewritten into one fixed set of fields, whichever site it came from. That is what lets the filters and the matcher treat a Reed advert and a small agency's advert in exactly the same way.
<table>
<thead><tr><th>Field</th><th>What it holds</th></tr></thead>
<tbody>
<tr><td>Title</td><td>The job title, as the site wrote it.</td></tr>
<tr><td>Employer</td><td>The company hiring, or the agency if the real employer isn't named.</td></tr>
<tr><td>Town and postcode</td><td>Used to work out the distance from the graduate's home.</td></tr>
<tr><td>Salary</td><td>Exactly as stated, and left blank if hidden. Never estimated.</td></tr>
<tr><td>Working pattern</td><td>Office, hybrid or remote, and the number of office days if given.</td></tr>
<tr><td>Closing date</td><td>So expired adverts can be dropped.</td></tr>
<tr><td>Requirements</td><td>The essential and desirable points, each with the sentence it came from.</td></tr>
<tr><td>Link</td><td>The address of the original advert.</td></tr>
<tr><td>Source and date seen</td><td>Which site it came from, and when we looked.</td></tr>
</tbody>
</table></li>
<li><strong>Save a snapshot</strong>
The computer saves everything it found, stamped with the date and time. That saved set is the snapshot. Adverts disappear from recruiters' sites without warning, so the snapshot is the only record of what was live on a given day. The design rebuilds it every night and drops adverts that have passed their closing date.</li>
<li><strong>Filter for the people using the app</strong>
This is where most of the work happens. SkillMatch's users are Code Institute graduates, mostly with no data experience but years in other careers, from project management to running a company. An advert has to pass every test below to reach them. Adverts that fail are kept and counted rather than deleted, so the app can say how many it hid and why.
<table>
<thead><tr><th>Test</th><th>What it drops</th><th>Status</th></tr></thead>
<tbody>
<tr><td>Area</td><td>Jobs outside the West Midlands, unless they are fully remote within the UK.</td><td><span class="pill built">Built</span></td></tr>
<tr><td>Role</td><td>Jobs that aren't data or analyst roles.</td><td><span class="pill built">Built</span></td></tr>
<tr><td>Level</td><td>Titles containing senior, lead, head of, director, manager, chief, principal or architect. "Junior Data Analyst" gets a boost instead.</td><td><span class="pill built">Built</span></td></tr>
<tr><td>Training courses</td><td>Adverts that are really selling a course.</td><td><span class="pill built">Built</span></td></tr>
<tr><td>Duplicates</td><td>The same job on several sites is grouped into one.</td><td><span class="pill built">Built</span></td></tr>
<tr><td>Professional qualifications</td><td>Roles that need a qualification such as ACCA, which a bootcamp graduate won't have.</td><td><span class="pill todo">Decided, not built</span></td></tr>
<tr><td>Fake adverts</td><td>Recruiters collecting CVs for jobs that may not exist, and adverts with no named employer.</td><td><span class="pill todo">Planned, as a daily check</span></td></tr>
</tbody>
</table></li>
<li><strong>Read the requirements</strong>
A parser reads the requirement sentences in each advert that survives. A parser is a program that turns ordinary text into labelled pieces. This one separates essential from desirable, tags each sentence with a skill (SQL, Excel, Power BI) or a competency (stakeholder management, problem solving), and notes whether the advert asks for data experience. It keeps the original sentence next to each tag, so the graduate can see the evidence for themselves.</li>
<li><strong>Match, show and link back</strong>
The matcher compares each advert with the graduate's own profile, requirement by requirement, and marks each one met, partly met or a gap. Adverts are sorted into Strong, Good, Stretch and Not yet, with a plain-English reason for each. The results card shows the title, employer, distance, the fit, and where the advert came from ("Job via Reed"). The click goes to the original advert, which is where the graduate applies. SkillMatch never handles the application.</li>
</ol>
<p class="callout">In data terms this is an ETL pipeline: Extract, Transform, Load. Steps 1 to 3 are Extract. Steps 4, 6 and 7 are Transform. Step 5 is Load, and step 8 is where the results reach the user. From the first live run, each run will also record how many adverts passed or failed each stage, so we can analyse what the pipeline did.</p>
<h2>Four ways to get adverts</h2>
<p>Not every site hands its adverts over the same way. SkillMatch uses four routes, and the list further down says which route each site gets.</p>
<table>
<thead><tr><th>Route</th><th>How it works</th><th>Good for</th><th>Limit</th></tr></thead>
<tbody>
<tr><td><strong>Official feed</strong></td><td>The site offers a side door for programs, called an API. A program asks a question and gets tidy data back instead of a web page.</td><td>Clean, reliable data. Used now for Reed, the four employer boards, We Work Remotely and Remote OK.</td><td>Only a few sites offer one. CV-Library's feed has been requested, with no reply yet.</td></tr>
<tr><td><strong>Reading the page</strong></td><td>Fetch the page, then use the site's recipe to pull out each advert. Also called scraping.</td><td>Works on almost any site, so it can cover the recruitment agencies.</td><td>One recipe per site. A redesign breaks the recipe.</td></tr>
<tr><td><strong>Links only</strong></td><td>No data is collected. The app builds a search link pre-filled with the graduate's town and sends them to the site.</td><td>No upkeep, and it never goes stale. The prototype has 87 of these today.</td><td>No filtering and no matching, because there is nothing to match.</td></tr>
<tr><td><strong>Typed in by hand</strong></td><td>A teammate finds an advert, checks it, and types the fields into a spreadsheet.</td><td>Sites where nothing else works.</td><td>Slow. The file <code>data/curated/adverts.csv</code> exists but is empty.</td></tr>
</tbody>
</table>
<h2>What the filters do to real numbers</h2>
<p>The Reed snapshot taken on 21 October shows the scale. The app pulled 2,565 West Midlands adverts from Reed. Of those, 64 reached the results page. Across every source, 77 did. That is about 2.5% of what was collected.</p>
<table>
<thead><tr><th>Main reason an advert was dropped</th><th>Reed adverts</th></tr></thead>
<tbody>
<tr><td>Not a data or analyst role</td><td>1,044</td></tr>
<tr><td>Outside the West Midlands</td><td>739</td></tr>
<tr><td>Too senior, by its title</td><td>643</td></tr>
<tr><td>A training course</td><td>64</td></tr>
</tbody>
</table>
<p class="aside">The counts come from the build report and are not a strict sequence, so don't add them up. They show where the weight sits. Collecting adverts is the easy part. Choosing the few worth showing is the job.</p>
<h2>What goes wrong</h2>
<ul>
<li><strong>A site changes its layout.</strong> The recipe stops finding adverts. Each site needs a check that fails loudly when it suddenly returns nothing.</li>
<li><strong>The page arrives empty.</strong> Many agency sites and company career pages build their list with JavaScript after the page loads, so the plain HTML has no adverts in it. Those need a tool that behaves like a real browser, which is slower and more fiddly.</li>
<li><strong>Some sites fight back.</strong> Indeed and LinkedIn actively block automated visitors. Skipping them and offering a search link is the sensible choice.</li>
<li><strong>The same job appears everywhere.</strong> One vacancy can be posted by the employer and by three agencies. Grouping by title, employer and town stops the graduate seeing it four times.</li>
<li><strong>Some adverts aren't real jobs.</strong> Agencies sometimes advertise a role to collect CVs. The planned daily check looks for adverts with no named employer and the same wording posted again and again.</li>
<li><strong>Adverts are badly written.</strong> About 17% of requirement sentences can't yet be tied to a skill. Another 15% are guesses, because the advert has no clear headings. The app shows them but never counts them against the graduate.</li>
</ul>
<h2>The full list, 96 websites</h2>
<p>Every site in the source register, grouped by type. The links open a current page for each source, usually a search page for data roles in the West Midlands. The first three groups are open because they matter most for graduates looking for entry-level roles.</p>
<ul class="tally"><li><span class="pill built">Built: 7</span></li><li><span class="pill wait">Feed requested: 1</span></li><li><span class="pill todo">To be read: 83</span></li><li><span class="pill skip">Unavailable: 1</span></li><li><span class="pill skip">Hard to read, suggest skipping: 2</span></li><li><span class="pill skip">Not used: 2</span></li></ul>
<p class="aside">Status key. <strong>Built</strong> means SkillMatch already collects from it. <strong>Feed requested</strong> means we have asked for a proper feed and are waiting. <strong>To be read</strong> means it needs a recipe and a fetch. <strong>Unavailable</strong> means the listed page returned 404 when checked on 30 October 2026. Reed is built through its official feed, and its pages can be read as well. The two sites marked for skipping are suggestions that Phil can overrule.</p>
<details class="group" open=""><summary>Recruitment agencies<span class="ct">21</span></summary><table><thead><tr><th>Website</th><th>Area it covers</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://www.robertwalters.co.uk/expertise/technology/data-analysis-and-business-intelligence-jobs.html">Robert Walters</a></td><td>West Midlands, Wider region, UK remote</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.amtis.co.uk/jobs/">Amtis</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.unitingpeople.co.uk/jobs">Uniting People</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.nigelfrank.com/microsoft-jobs">Nigel Frank / Tenth Revolution</a></td><td>West Midlands, Wider region, UK remote</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.hendersonscott.co.uk/jobs/">Henderson Scott</a></td><td>West Midlands, Hybrid</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.workwithglee.com/candidates/job-search/">Gleeson Recruitment Group</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.networkitr.co.uk/jobs/">Network IT</a></td><td>West Midlands, Wider region</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.sfpartners.com/">SF Partners / SF Recruitment</a></td><td>West Midlands, Wider region</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.harnham.com/job-search/?_keyword=Birmingham">Harnham</a></td><td>West Midlands, Wider region</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://viqu.co.uk/jobs/?results=1">VIQU</a></td><td>UK remote, UK-wide</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://crimson.co.uk/">Crimson</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.rebelrecruiters.co.uk/">Rebel Recruiters</a></td><td>Wider region, Hybrid</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.kdrtalentsolutions.com/en/job-results">KDR Talent Solutions</a></td><td>West Midlands, UK-wide</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.experis.co.uk/">Experis</a></td><td>Wider region, UK remote</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.oscar-recruit.com/">Oscar</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://jobs.ashdowngroup.com/jobs.aspx">Ashdown Group</a></td><td>Remote, West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.michaelpage.co.uk/jobs/data-analysis/west-midlands-west-midlands">Michael Page</a></td><td>West Midlands, Wider region</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.roberthalf.com/gb/en">Robert Half</a></td><td>Wider region</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.hays.co.uk/job-search/data-analyst-jobs-in-birmingham-uk">Hays</a></td><td>West Midlands, UK-wide</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.pertemps.co.uk/jobs/data-analyst-jobs">Pertemps</a></td><td>West Midlands, Wider region, UK-wide</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.adecco.com/en-gb">Adecco</a></td><td>West Midlands, UK-wide</td><td><span class="pill todo">To be read</span></td></tr></tbody></table></details>
<details class="group" open=""><summary>Specialist job boards<span class="ct">8</span></summary><table><thead><tr><th>Website</th><th>Area it covers</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://www.cwjobs.co.uk/jobs/data-quality/in-west-midlands">CWJobs</a></td><td>West Midlands, Wider region</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.itjobswatch.co.uk/find/Data-Engineer-jobs-in-West-Midlands">IT Jobs Watch</a></td><td>West Midlands, Wider region</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.technojobs.co.uk/data-analyst-jobs/birmingham">Technojobs</a></td><td>West Midlands, UK-wide</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://devitjobs.uk/jobs/Data/all">DevITjobs</a></td><td>UK-wide, Remote</td><td><span class="pill todo">To be read</span></td></tr><tr><td>DataAnalystJobs.io</td><td>UK-wide, Remote</td><td><span class="pill skip">Unavailable</span></td></tr><tr><td><a href="https://www.dataanalystjobs.co.uk/browse-jobs/">DataAnalystJobs.co.uk</a></td><td>UK-wide, Remote</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.welcometothejungle.com/en/pages/jobs-data-analyst-uk">Welcome to the Jungle / Otta</a></td><td>UK-wide, Remote</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://wellfound.com/jobs">Wellfound</a></td><td>UK remote</td><td><span class="pill todo">To be read</span></td></tr></tbody></table></details>
<details class="group" open=""><summary>General job boards<span class="ct">7</span></summary><table><thead><tr><th>Website</th><th>Area it covers</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://www.reed.co.uk/jobs/junior-data-analyst-sql-power-bi-jobs-in-birmingham">Reed</a></td><td>West Midlands, Wider region, UK-wide</td><td><span class="pill built">Built</span></td></tr><tr><td><a href="https://www.cv-library.co.uk/data-analyst-jobs-in-west-midlands">CV-Library</a></td><td>West Midlands, Wider region, UK remote</td><td><span class="pill wait">Feed requested</span></td></tr><tr><td><a href="https://www.totaljobs.com/jobs/data-analyst/in-west-midlands">Totaljobs</a></td><td>West Midlands, Wider region</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.jobsite.co.uk/jobs/data-analyst/in-west-midlands">Jobsite</a></td><td>West Midlands, Wider region</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://jobserve.com/gb/en/Job-Search/">JobServe</a></td><td>West Midlands, Wider region, UK-wide</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://uk.indeed.com/q-data-analyst-l-west-midlands-jobs.html">Indeed</a></td><td>West Midlands, Wider region, UK-wide</td><td><span class="pill skip">Hard to read, suggest skipping</span></td></tr><tr><td><a href="https://www.linkedin.com/jobs/">LinkedIn Jobs</a></td><td>West Midlands, Wider region, UK-wide, Remote, check UK eligibility</td><td><span class="pill skip">Hard to read, suggest skipping</span></td></tr></tbody></table></details>
<details class="group"><summary>Graduate boards<span class="ct">4</span></summary><table><thead><tr><th>Website</th><th>Area it covers</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://www.gradcracker.com/search/computing-technology/data-science-graduate-jobs">Gradcracker</a></td><td>West Midlands, Wider region, UK-wide</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.brightnetwork.co.uk/graduate-jobs/technology/in-birmingham/">Bright Network</a></td><td>West Midlands, UK-wide</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.prospects.ac.uk/browse-graduate-jobs/all-sectors/west-midlands-59">Prospects</a></td><td>Wider region, UK-wide</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://targetjobs.co.uk/graduate-jobs">targetjobs</a></td><td>UK-wide</td><td><span class="pill todo">To be read</span></td></tr></tbody></table></details>
<details class="group"><summary>Sector boards<span class="ct">2</span></summary><table><thead><tr><th>Website</th><th>Area it covers</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://www.jobs.ac.uk/categories/data-analyst-jobs?sort-order=closing-date">jobs.ac.uk</a></td><td>West Midlands, Wider region, UK-wide</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.charityjob.co.uk/data-jobs-in-birmingham_west-midlands">CharityJob</a></td><td>West Midlands, UK remote</td><td><span class="pill todo">To be read</span></td></tr></tbody></table></details>
<details class="group"><summary>Remote job boards<span class="ct">3</span></summary><table><thead><tr><th>Website</th><th>Area it covers</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://weworkremotely.com/remote-job-rss-feed">We Work Remotely</a></td><td>Remote, check UK eligibility</td><td><span class="pill built">Built</span></td></tr><tr><td><a href="https://remoteok.com/">Remote OK</a></td><td>Remote, check UK eligibility</td><td><span class="pill built">Built</span></td></tr><tr><td><a href="https://www.workingnomads.com/jobs">Working Nomads</a></td><td>Remote, check UK eligibility</td><td><span class="pill todo">To be read</span></td></tr></tbody></table></details>
<details class="group"><summary>Aggregators<span class="ct">2</span></summary><table><thead><tr><th>Website</th><th>Area it covers</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://developer.adzuna.com/overview">Adzuna</a></td><td>UK-wide, Remote</td><td><span class="pill skip">Not used</span></td></tr><tr><td><a href="https://uk.jooble.org/api/about">Jooble</a></td><td>UK-wide, Remote</td><td><span class="pill skip">Not used</span></td></tr></tbody></table></details>
<details class="group"><summary>Public job portals<span class="ct">4</span></summary><table><thead><tr><th>Website</th><th>Area it covers</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://www.jobs.nhs.uk/candidate/search/results?keyword=data+analyst&amp;language=en">NHS Jobs</a></td><td>West Midlands, Wider region, UK-wide</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.wmjobs.co.uk/">WMJobs</a></td><td>West Midlands, Wider region</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.civilservicejobs.service.gov.uk/csr/index.cgi">Civil Service Jobs</a></td><td>West Midlands, Wider region, UK-wide, Hybrid</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.gov.uk/find-a-job">Find a job / DWP Work Hub</a></td><td>West Midlands, UK-wide</td><td><span class="pill todo">To be read</span></td></tr></tbody></table></details>
<details class="group"><summary>Employers with their own job pages<span class="ct">17</span></summary><table><thead><tr><th>Website</th><th>Area it covers</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://careers.jlr.com/early-careers/graduates/graduate-data-analytics-cross-functional">JLR</a></td><td>West Midlands, Wider region</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://careers.nfumutual.co.uk/what-you-could-be-doing/analytics">NFU Mutual</a></td><td>Wider region</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://careers.pageuppeople.com/806/cw/en/search/?search-keyword=data">Halfords</a></td><td>Wider region</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://careers.mandmdirect.com/">MandM</a></td><td>Wider region</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.bet365careers.com/all-jobs">bet365</a></td><td>Wider region</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://jobsearch.tarmac.com/">Tarmac / CRH</a></td><td>West Midlands, UK-wide</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.capgemini.com/gb-en/careers/join-us/">Capgemini</a></td><td>Wider region</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://careers.serco.com/gb/en">Serco</a></td><td>West Midlands, UK-wide</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.dudleybuildingsociety.co.uk/about-us/careers/current-roles/">Dudley Building Society</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.hsbc.com/careers/students-and-graduates/find-a-programme?area-of-interest=data-analytics&amp;page=1&amp;take=40">HSBC</a></td><td>West Midlands, UK-wide</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://lbg.wd3.myworkdayjobs.com/LBG_Careers">Lloyds Banking Group</a></td><td>West Midlands, UK-wide</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.careers.severntrent.com/go/CORPORATE-FUNCTIONS-JOBS/8578002/">Severn Trent</a></td><td>West Midlands, Wider region</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://jobs.nationalgrid.com/uk/jobs?countries=United+Kingdom&amp;page=1&amp;pagesize=10">National Grid</a></td><td>Wider region, UK-wide</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://apply.workable.com/biffa/">Biffa</a></td><td>West Midlands, UK-wide</td><td><span class="pill built">Built</span></td></tr><tr><td><a href="https://careers.isio.com/jobs">Isio</a></td><td>West Midlands, UK-wide</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://job-boards.greenhouse.io/gymshark">Gymshark</a></td><td>West Midlands</td><td><span class="pill built">Built</span></td></tr><tr><td><a href="https://careers.globaldata.com/">GlobalData</a></td><td>UK-wide, Remote</td><td><span class="pill todo">To be read</span></td></tr></tbody></table></details>
<details class="group"><summary>Remote-first employers<span class="ct">4</span></summary><table><thead><tr><th>Website</th><th>Area it covers</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://jobs.lever.co/kpler/?location=United+Kingdom">Kpler</a></td><td>Hybrid</td><td><span class="pill built">Built</span></td></tr><tr><td><a href="https://job-boards.greenhouse.io/monzo">Monzo</a></td><td>UK remote</td><td><span class="pill built">Built</span></td></tr><tr><td><a href="https://automattic.com/work-with-us/">Automattic</a></td><td>Remote, check UK eligibility</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://about.gitlab.com/jobs/">GitLab</a></td><td>UK remote</td><td><span class="pill todo">To be read</span></td></tr></tbody></table></details>
<details class="group"><summary>Public bodies, NHS and universities<span class="ct">9</span></summary><table><thead><tr><th>Website</th><th>Area it covers</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://careers.wmca.org.uk/jobs/search">West Midlands Combined Authority</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://careers.coventry.gov.uk/jobs/search">Coventry City Council</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://careers.staffordshire.gov.uk/jobs/search">Staffordshire County Council</a></td><td>Wider region</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.birmingham.ac.uk/Jobs">University of Birmingham</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://workwithus.warwick.ac.uk/?locale=en_GB">University of Warwick</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://jobs.aston.ac.uk/Vacancies.aspx">Aston University</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.bsmhft.nhs.uk/join-us/">Birmingham and Solihull Mental Health NHS Foundation Trust</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://jobs.uhb.nhs.uk/">University Hospitals Birmingham</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.westmidlands.police.uk/police-forces/west-midlands-police/areas/careers/wmp-jobs/">West Midlands Police</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr></tbody></table></details>
<details class="group"><summary>Councils<span class="ct">10</span></summary><table><thead><tr><th>Website</th><th>Area it covers</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://www.dudley.gov.uk/jobs-and-careers">Dudley Council</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://go.walsall.gov.uk/jobs-and-careers-/job-vacancies">Walsall Council</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.sandwell.gov.uk/jobs/vacancies">Sandwell Council</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.wolverhampton.gov.uk/jobs-and-careers/job-vacancies">City of Wolverhampton Council</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.birmingham.gov.uk/jobs">Birmingham City Council</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.solihull.gov.uk/jobs-and-training">Solihull Council</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.herefordshire.gov.uk/jobs-skills-and-opportunities/">Herefordshire Council</a></td><td>Wider region</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://next.shropshire.gov.uk/jobs-and-careers/">Shropshire Council</a></td><td>Wider region</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://careers.worcestershire.gov.uk/jobs/search">Worcestershire County Council</a></td><td>Wider region</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.warwickshire.gov.uk/jobs">Warwickshire County Council</a></td><td>Wider region</td><td><span class="pill todo">To be read</span></td></tr></tbody></table></details>
<details class="group"><summary>Housing associations<span class="ct">3</span></summary><table><thead><tr><th>Website</th><th>Area it covers</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://jobs.midlandheartgroup.org.uk/jobs/home/">Midland Heart</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://www.platformhg.com/apprenticeships">Platform Housing Group</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr><tr><td><a href="https://greensquareaccord.co.uk/about/work-with-us/careers">GreenSquareAccord</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr></tbody></table></details>
<details class="group"><summary>Charities<span class="ct">1</span></summary><table><thead><tr><th>Website</th><th>Area it covers</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://www.faresharemidlands.org.uk/job-vacancies/junior-data-analyst">FareShare Midlands</a></td><td>West Midlands</td><td><span class="pill todo">To be read</span></td></tr></tbody></table></details>
<details class="group"><summary>Application-system directories<span class="ct">1</span></summary><table><thead><tr><th>Website</th><th>Area it covers</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://apps.trac.jobs/">Trac</a></td><td>West Midlands, Wider region, UK-wide</td><td><span class="pill todo">To be read</span></td></tr></tbody></table></details>
<h2>Words used on this page</h2>
<dl class="gloss">
<dt>API</dt><dd>A side door a website provides for programs. You send a request and get structured data back instead of a web page.</dd>
<dt>Duplicate</dt><dd>The same vacancy advertised on more than one site, or more than once on the same site.</dd>
<dt>ETL</dt><dd>Extract, Transform, Load. Fetch the raw data, clean and reshape it, then store it where the analysis can use it.</dd>
<dt>HTML</dt><dd>The code a web page is written in. Text is wrapped in tags such as <code>h3</code> for a heading or <code>a</code> for a link.</dd>
<dt>JSON</dt><dd>A plain-text way of storing structured lists. The source register is a JSON file.</dd>
<dt>Parser</dt><dd>A program that reads text and turns it into labelled pieces, such as splitting an advert into essential and desirable requirements.</dd>
<dt>Register</dt><dd>The master list of websites SkillMatch reads, with notes on each one.</dd>
<dt>Scraping</dt><dd>Fetching a web page with a program and pulling the information out of its code.</dd>
<dt>Selector</dt><dd>The recipe that says where on a page a piece of information sits, such as "the town is the span marked town".</dd>
<dt>Snapshot</dt><dd>What the sites were advertising at one moment, saved with the date and time.</dd>
<dt>URL</dt><dd>A web address, such as the text you type into a browser's address bar.</dd>
</dl>
<p class="done-when"><strong>Done when:</strong> you can explain, in your own words, what happens between a recruiter's website and a card on the results page, and name three reasons an advert would be dropped on the way.</p>""")

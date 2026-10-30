
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


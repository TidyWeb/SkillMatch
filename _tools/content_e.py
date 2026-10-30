
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

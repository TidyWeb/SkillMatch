# GitHub for Team Projects: A Beginner-Friendly Guide

A practical guide to collaborating safely on a shared GitHub project.

## 1. What are Git and GitHub?

**Git** is a version-control tool. It records changes to your files over
time, allowing you to see what changed, who changed it, and restore
earlier versions when needed.

**GitHub** is an online platform that hosts Git repositories so multiple
people can work on the same project.

-   **Git** keeps track of the history.
-   **GitHub** hosts the shared project online.
-   **VS Code** is where you can edit your code and use Git.
-   **The terminal** is where you can enter Git commands.
-   **GitHub Projects** is a planning board for tasks, separate from the
    code itself.

## 2. Essential terminology

  -----------------------------------------------------------------------
  Term                                Meaning
  ----------------------------------- -----------------------------------
  Repository (repo)                   The project folder and its version
                                      history.

  Local repository                    Your copy of the project on your
                                      computer.

  Remote repository                   The shared copy hosted on GitHub.

  Branch                              A separate line of development
                                      where you can work without
                                      immediately changing the main
                                      branch.

  `main`                              The branch commonly used for the
                                      main, stable version of a project.

  Commit                              A saved checkpoint of selected
                                      changes, with a message explaining
                                      what changed.

  Push                                Sending your local commits to
                                      GitHub.

  Pull                                Fetching changes from GitHub and
                                      integrating them into your current
                                      branch.

  Fetch                               Checking for new changes on GitHub
                                      without integrating them into your
                                      current branch.

  Merge                               Combining changes from one branch
                                      into another.

  Pull request (PR)                   A request to review and merge
                                      changes into another branch.

  Merge conflict                      A situation where Git cannot
                                      automatically determine how to
                                      combine changes.

  Clone                               Downloading a repository to your
                                      computer for the first time.

  Stage                               Selecting which changes will be
                                      included in a commit.

  Revert                              Creating a new commit that undoes
                                      the changes introduced by an
                                      earlier commit.

  Reset                               Moving a branch pointer to an
                                      earlier commit; depending on the
                                      options, this can also discard or
                                      unstage changes. Use carefully.

  `.gitignore`                        A file specifying files Git should
                                      not track, such as environment
                                      files or temporary outputs.
  -----------------------------------------------------------------------

**Remember:** A commit saves a checkpoint locally; a push uploads your
commits to GitHub.

## 3. The normal team workflow

For a small team, the safest approach is to work on separate branches
and merge completed work into `main` after checking it.

### Step 1 --- Get the latest changes

Open the terminal in your project folder:

``` bash
git switch main
git pull origin main
```

This switches you to `main` and retrieves the latest changes from
GitHub. If you have uncommitted changes, Git may prevent you from
switching branches. Check your status first and safely save or set aside
your work.

### Step 2 --- Create your own branch

``` bash
git switch -c feature/job-matching
```

Use a short, descriptive name, such as `feature/dashboard`,
`fix/data-cleaning` or `docs/readme`. A branch gives you a separate
place to develop your feature.

### Step 3 --- Make and check your changes

Edit the relevant files in VS Code, then inspect your changes:

``` bash
git status
git diff
```

-   `git status` tells you which files have changed.
-   `git diff` shows changes to tracked files that have not yet been
    staged.

### Step 4 --- Stage and commit your work

``` bash
git add path/to/your_file.py
git commit -m "Add job matching logic"
```

Replace the example path with the file you changed. You can stage
several specific files at once. Use `git add .` only after checking that
you are not including unwanted files, such as API keys, temporary data
or unrelated changes.

Good commit messages include `Clean duplicate job listings`,
`Add location filter`, `Fix missing salary values` and
`Update project setup instructions`. Avoid vague messages such as
`stuff` or `final final version`.

### Step 5 --- Push your branch to GitHub

``` bash
git push -u origin feature/job-matching
```

This uploads your branch and its commits to GitHub. The `-u` option sets
the upstream relationship, making future pushes from that branch
simpler.

### Step 6 --- Open a pull request

On GitHub:

1.  Open the repository.
2.  Create a pull request for your branch.
3.  Check that the **base** is `main` and the **compare** branch is your
    feature branch.
4.  Explain what you changed and how you tested it.
5.  Ask a teammate to review it.
6.  Merge it when the changes are ready.

After merging, check that the updated `main` works before building
further features on top of it.

## 4. How should four collaborators work together?

Agree on a few simple rules before everyone starts coding.

1.  **Give each task an owner.** Record the owner, expected output and
    acceptance criteria on the project board.
2.  **Use separate branches.** Avoid everyone editing the same files on
    `main`.
3.  **Keep commits focused.** A commit should ideally represent one
    coherent change.
4.  **Communicate about shared files.** If two people need to change the
    same notebook, app file or data-cleaning script, agree on who will
    do what first.
5.  **Review before merging.** Another teammate should check the changes
    when time permits.
6.  **Integrate early.** Do not wait until the final day to combine
    everyone's code.
7.  **Never commit secrets.** Keep API keys and passwords out of GitHub.
    Use environment variables and a local `.env` file listed in
    `.gitignore`.

For a short hackathon, a lightweight rule is enough: one branch per
task, one owner per branch, and frequent integration into `main`.

> **Team rule:** Nobody merges into `main` without checking that the
> combined project still runs. This helps catch integration problems
> before they affect the team's main version.

## 5. What is a merge conflict?

A merge conflict occurs when Git cannot automatically combine two sets
of changes.

For example, two collaborators edit the same lines of `app.py`: one
changes the title to `Job Match Dashboard`, while the other changes it
to `Career Match Tool`. Git cannot know which version the team wants.

### How to resolve a conflict in VS Code

First, make sure your work is committed or otherwise safely backed up.
When Git reports a conflict, open the affected file. You may see markers
like these:

``` text
<<<<<<< HEAD
Job Match Dashboard
=======
Career Match Tool
>>>>>>> feature/dashboard
```

-   `<<<<<<< HEAD` starts the version from your current branch.
-   `=======` separates the two versions.
-   `>>>>>>> ...` marks the incoming version.

VS Code may offer buttons such as **Accept Current Change**, **Accept
Incoming Change** and **Accept Both Changes**. The exact wording can
vary.

Choose the correct option, or manually edit the file to combine the
changes sensibly. Do not blindly choose one side without checking what
it does.

Then:

1.  Remove all conflict markers.
2.  Check that the file contains the intended final result.
3.  Run the code or tests.
4.  Stage the resolved file.
5.  Complete the merge or continue the operation Git started.

``` bash
git add path/to/conflicted_file.py
```

If Git was performing a merge, finish it with:

``` bash
git commit
```

Git may open an editor for the merge message. Save and close it, or use
the message Git supplies.

If the conflict occurred during a rebase, use `git rebase --continue`
instead. First check which operation Git says is in progress.

**Important:** The correct solution preserves the intended behaviour of
the changes; do not simply delete the markers and keep a random version.
If unsure, ask the teammate who wrote the conflicting code.

## 6. What if Git says your push was rejected?

This can mean that someone else has pushed changes that your local
branch does not contain. Do not immediately force-push, as this can
overwrite other people's work.

If you are working on a feature branch, start by checking the state:

``` bash
git fetch origin
git status
```

If it fits your team's workflow, integrate the latest `main` into your
feature branch:

``` bash
git merge origin/main
```

Resolve conflicts, test the code, and push your branch again:

``` bash
git push
```

If the rejection happened while pushing `main`, stop and inspect the
situation rather than trying to overwrite the remote branch. Coordinate
with your teammates.

## 7. How do I go back to an earlier version?

Choose the method based on what you want to undo.

### Option A --- See the project's history

``` bash
git log --oneline
```

This displays recent commits, their short IDs and messages. Example:

``` text
a1b2c3d Add location filter
e4f5g6h Clean vacancy data
i7j8k9l Create initial dashboard
```

Your actual IDs will be different.

### Option B --- Undo an earlier commit safely with `git revert`

If a commit has already been shared with the team, this is usually the
safest way to undo it:

``` bash
git revert a1b2c3d
git push
```

Replace `a1b2c3d` with the actual commit ID. Git creates a **new
commit** that reverses the selected commit's changes, preserving the
existing history. If the revert produces conflicts, resolve and test
them before completing the operation.

### Option C --- Temporarily inspect an earlier version

``` bash
git switch --detach a1b2c3d
```

This lets you inspect files at that point in history without moving your
main branch. You are in a detached state, not a normal working branch.
To return to `main`:

``` bash
git switch main
```

If you want to continue developing from that old checkpoint, create a
new branch from it.

### Option D --- Move a branch back with `git reset`

``` bash
git reset --hard a1b2c3d
```

**Warning:** `--hard` discards uncommitted changes and makes tracked
files match the selected commit. It can also remove later commits from
the current branch's visible history. Do not use it casually, especially
on shared branches.

For beginners, prefer `git revert` when undoing a commit that has
already been shared.

### Option E --- Restore one file from an earlier version

Inspect the earlier version first:

``` bash
git show a1b2c3d:path/to/file.py
```

To restore that file from the earlier commit into your current working
tree:

``` bash
git restore --source=a1b2c3d -- path/to/file.py
```

Check the resulting changes before staging and committing them. This
restores one file, not the whole project.

## 8. What should I do if something goes wrong?

  -----------------------------------------------------------------------
  Situation                           First action
  ----------------------------------- -----------------------------------
  I do not know what I changed        Run `git status` and `git diff`.

  My push was rejected                Run `git fetch origin` and inspect
                                      the branch status. Do not
                                      force-push.

  I have a merge conflict             Open the affected files and resolve
                                      the competing changes carefully.

  I committed the wrong files but     Stop and inspect the commit and
  have not pushed                     working tree before changing
                                      history.

  I need to undo a shared commit      Consider `git revert`.

  I accidentally deleted code         Stop making changes. Inspect
                                      `git status` and `git log` before
                                      attempting recovery.

  I am unsure what a command will do  Ask a teammate before running
                                      destructive commands.
  -----------------------------------------------------------------------

Useful diagnostic commands:

``` bash
git status
git log --oneline -10
git diff
git branch
```

These help you understand the current state before making further
changes.

## 9. Team checklist

### Before starting work

-   [ ] Check the project board and agree on your task.
-   [ ] Switch to the appropriate branch.
-   [ ] Pull the latest changes when appropriate.
-   [ ] Check that you are not carrying unrelated uncommitted changes.

### Before committing

-   [ ] Review the files you changed.
-   [ ] Run the code or relevant tests.
-   [ ] Stage only the files you intend to commit.
-   [ ] Write a clear commit message.
-   [ ] Check that no credentials or unwanted files are included.

### Before merging

-   [ ] Confirm that the pull request targets the correct branch.
-   [ ] Review the changes and check for conflicts.
-   [ ] Test the integrated code.
-   [ ] Tell the team when the feature is ready.
-   [ ] Update the project board.

## 10. The golden rules

1.  Commit regularly, but keep commits meaningful.
2.  Pull and integrate changes regularly.
3.  Use branches to keep work separate until it is ready.
4.  Never assume a successful commit means the code works.
5.  Never force-push to a shared branch without explicit team agreement.
6.  Do not use destructive commands unless you understand their effects.
7.  If in doubt, stop, check the status, and ask before making things
    worse.

**The main principle:** Git is designed to help you recover from
mistakes, but the safest recovery depends on understanding which changes
are local, which have been shared, and which belong to other
collaborators.

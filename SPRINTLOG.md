# Robo-Arena Changelog

## Sprint 1

Branch protection on `main`:

- require pull request before merging
  - require approval
  - approvals don't become stale with new commits to speed up review process. Changed when bugs are introduced hereby.
- require status checks to pass before merging
- require branch to be up to date. Prevents bugs introduced in merge commits
- require conversion resolution
- require linear history. For easier understanding of history.
- allow force pushes. As per sprint spec.

# Sprintlog 1

## Branch protection on `main`:

_[@weiserhase](https://github.com/uni-tj/robo-arena/commits?author=weiserhase) (Jan Keller), [@p-98](https://github.com/uni-tj/robo-arena/commits?author=p-98) (Timon Martins)_

- require pull request before merging
  - require approval
  - approvals don't become stale with new commits to speed up review process. Changed when bugs are introduced hereby.
- require status checks to pass before merging
- require branch to be up to date -> prevents bugs introduced in merge commits
- require conversation resolution
- require linear history -> for easier understanding of history.

## GitHub actions:

_[@weiserhase](https://github.com/uni-tj/robo-arena/commits?author=weiserhase) (Jan Keller), [@p-98](https://github.com/uni-tj/robo-arena/commits?author=p-98) (Timon Martins)_
- on push and pull-request test:
  - check formatting with black -> smaller diffs
  - Lint tests with flake8 
  - run unit tests with pytest
  - check conventional commit compliance with cocogitto -> allow to autogenerate a changelog
- git hooks on commit (locally)
  - execute all the checks run in ci -> faster feedback & dev cycle
  
## GitHub pages:

_[@weiserhase](https://github.com/uni-tj/robo-arena/commits?author=weiserhase) (Jan Keller), [@p-98](https://github.com/uni-tj/robo-arena/commits?author=p-98) (Timon Martins)_
- use markdown files for easier & faster writing
- deploy pages on push to main
- autogenerate changelog for current commit

## Python setup

_[@weiserhase](https://github.com/uni-tj/robo-arena/commits?author=weiserhase) (Jan Keller), [@p-98](https://github.com/uni-tj/robo-arena/commits?author=p-98) (Timon Martins), [@JulesOxe](https://github.com/uni-tj/robo-arena/commits?author=JulesOxe) (Julius Oexle)_
- use pipenv for easy and reproducible builds
- use black for formatting 
- use flake8 for linting
- use pytest for unit tests

## Create a first mini game:

_[@JulesOxe](https://github.com/uni-tj/robo-arena/commits?author=JulesOxe) (Julius Oexle)_
- init a snake game:
  - snake can move over the display and can be controlled via keyboard
  - player can collect fruits to grow the snake and earn points
  - if fruit is collected, it spawns new on a random place
  - if snake collides with itself, the game is over and an endscreen displays the score
  
_[@weiserhase](https://github.com/uni-tj/robo-arena/commits?author=weiserhase) (Jan Keller)_
- refactor snake game:
  - refactor code with data-types and classes  
  - use new datatypes to simplify game logic and make the code more extesible
  
_[@p-98](https://github.com/uni-tj/robo-arena/commits?author=p-98) (Timon Martins)_
- fix fruit generation in case there is no free tile
- add different game endings:
  - you can lose -> snake collides with itself
  - you can win -> snake is big as the screen and no new fruit can spawn
  - you can quit -> closing the window
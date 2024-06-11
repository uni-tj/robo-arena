# Sprintlog 4

## Merge Prototypes

_[@weiserhase](https://github.com/uni-tj/robo-arena/commits?author=weiserhase) (Jan Keller), [@p-98](https://github.com/uni-tj/robo-arena/commits?author=p-98) (Timon Martins), [@JulesOxe](https://github.com/uni-tj/robo-arena/commits?author=JulesOxe) (Julius Oexle)_

After we worked on the three seperate prototypes (game core, rendering, level generation), this time we went ahead and merged all of them.  
Doing this, we had to tackle the following challenges:

- Due to differences in directory structure, we had to rename and move around many files.
  We agreed on the client/server/shared distinction and moved rendering to shared while level generation went into server.
  Afterwards we had to do the tedious task of adapting all the imports.
  In addition we moved the codebase into a python package (required for proper testing) which further increased the amount of import refactoring.
- To simulate interfaces to other prototypes, we used dummy implementations.
  Of course, the dummy implementations diverged from the actual implementations over time.
  When merging the prototypes, this resulted in some neccessary changes in different parts of the project.
- While moving the main types into one file (shared/types.py), we ended up with cyclomatic imports of types.
  This had to be solved by using 'type imports', like so:

  ```python
  from typing import TYPE_CHECKING

  if TYPE_CHECKING
    from ... import MyType
  ```

- To reduce coupling and provide more modular interface between different parts of the software, we introduced the class `EventTarget`.
  This provides an interface to subscribe to typed event of entities, etc.
  The first use was to register the rendering engine to window resize events.
- In the level generation prototype, the interface was pretty low-level. To increase readability and ease of use in the server,
  an abstraction called `LevelGenerator` was introduced.

## Future Plans (Project Board)

_[@weiserhase](https://github.com/uni-tj/robo-arena/commits?author=weiserhase) (Jan Keller), [@p-98](https://github.com/uni-tj/robo-arena/commits?author=p-98) (Timon Martins), [@JulesOxe](https://github.com/uni-tj/robo-arena/commits?author=JulesOxe) (Julius Oexle)_

In the beginning of the project we noted down what the game is supposed to become. What we didn't figure you yet, was _how_ to get there, in other words:
What is technically needed for our game, specifically the minimum viable product?  
After we now have a basic game running, we realized we didn't quite know what was important to implement next.

So we took several meetings and quite some time to setup a [project board](https://github.com/orgs/uni-tj/projects/3) and further sketch out our upcoming tasks.
It is based on the minimum viable product we defined in [sprintlog 2](sprintlog-2.md).  
The ultimate goal was to spend some time now, but save time over the next sprints, because we now have a list of tasks to work on.
We explicitly thought about how to manage complex tasks such as room state, game state, etc.
Last but not least we labelled the tasks, created milestones and are now ready to go for the next few weeks.

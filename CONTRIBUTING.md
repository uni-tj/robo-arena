# Installation

Clone repository:

```sh
git clone https://github.com/uni-tj/robo-arena
```

Install git hooks:

```sh
cog install-hook --all
```

# Submitting PR

The naming convention for branches is:

```
type/[scope/]/topic
```

where type and optional scope match their conventional commits meaning. All parts are [kebab-case](https://angular.io/guide/glossary#case-types).

# Project Structure

This game is roughly splitted in three parts:

- Server
  - Level generation
  - Room logic
  - Spawning/deleting entities
  - Sending updates to clients
- Client
  - Predict movement, for smooth network experience
  - Receivee updates from server
  - Call rendering
- Shared, common code needed on both server and client
  - Movement logic, so that client-side prediction and server calculations match exactly
  - Rendering, so that we could visualize the server state
  - Utilities, like collections, vectors, ...

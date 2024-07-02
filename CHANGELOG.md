## Unreleased ([8a75c40..efee37e](https://github.com/uni-tj/robo-arena/compare/8a75c40..efee37e))
#### Bug Fixes
- **(rendering)** move cache clear to ctx creation - ([efee37e](https://github.com/uni-tj/robo-arena/commit/efee37e6a3c1bcd812f782e7d566e7979f2ff28e)) - [@p-98](https://github.com/p-98)
#### Features
- **(client)** track mouse position - ([48aa81c](https://github.com/uni-tj/robo-arena/commit/48aa81ce0614aa9ffd97a30ab7c5f0357198bd8a)) - [@p-98](https://github.com/p-98)
- quit gracefully - ([b41de52](https://github.com/uni-tj/robo-arena/commit/b41de5248e113c2fd58e282d29679efd89b89ead)) - [@p-98](https://github.com/p-98)
#### Miscellaneous Chores
- reduce debug logs - ([45266c7](https://github.com/uni-tj/robo-arena/commit/45266c7c2c9333e8389deb6f5576eeb61bc37b9d)) - [@p-98](https://github.com/p-98)
#### Refactoring
- **(rendering)** cleanup & simplify rendering - ([b0008e9](https://github.com/uni-tj/robo-arena/commit/b0008e9bcaa6ce1a59754a14adccfc549f0b1b42)) - [@p-98](https://github.com/p-98)
- **(shared)** EventTarget shorted method names - ([1ac2493](https://github.com/uni-tj/robo-arena/commit/1ac2493baed975f90317d6bba3ad9f19926dbc2e)) - [@p-98](https://github.com/p-98)

- - -

## [0.5.0](https://github.com/uni-tj/robo-arena/compare/0.4.0..0.5.0) - 2024-06-26
#### Documentation
- sprintlog 5 - ([8a75c40](https://github.com/uni-tj/robo-arena/commit/8a75c403e1c6ea4873874049d631704d13fee8a0)) - [@p-98](https://github.com/p-98)
#### Miscellaneous Chores
- remove snake - ([067221a](https://github.com/uni-tj/robo-arena/commit/067221a547597a1177a867a2ff38a02299c8d603)) - [@p-98](https://github.com/p-98)
#### Refactoring
- **(rendering)** make renderctx internal - ([9606934](https://github.com/uni-tj/robo-arena/commit/9606934db6a5838826a3e31ba0fabe71517a3881)) - [@JulesOxe](https://github.com/JulesOxe)

- - -

## [0.4.0](https://github.com/uni-tj/robo-arena/compare/0.3.0..0.4.0) - 2024-06-11
#### Bug Fixes
- **(ui)** render performance - ([ace263e](https://github.com/uni-tj/robo-arena/commit/ace263ed8b59be67c6359d6828e6b17e72df7c80)) - [@p-98](https://github.com/p-98)
- **(wfc)** change function to allow for grid expansion - ([b24c399](https://github.com/uni-tj/robo-arena/commit/b24c399b1de3372a4a1556385cdbf7f2cec70ebd)) - [@weiserhase](https://github.com/weiserhase)
#### Documentation
- sprintlog 4 - ([a8397c9](https://github.com/uni-tj/robo-arena/commit/a8397c9a56cdb20ae2bd605755f87086d84ae28e)) - [@p-98](https://github.com/p-98)
#### Features
- **(level-generation)** add basic level processing to convert the wfc output to renderable Blocks - ([f3e4216](https://github.com/uni-tj/robo-arena/commit/f3e42163e71c0e7fb9702ca0a8f21f1c9d34c646)) - [@weiserhase](https://github.com/weiserhase)
- **(shared)** collision detection framework - ([6f37685](https://github.com/uni-tj/robo-arena/commit/6f376853affd3c2c82e5d4e73f828370c629ef1f)) - [@p-98](https://github.com/p-98)
- **(wfc)** Wafe function collapse working prototype - ([94e35aa](https://github.com/uni-tj/robo-arena/commit/94e35aa5c50807f2aac13487562ceec9916c8fa6)) - [@weiserhase](https://github.com/weiserhase)
- render-engine - ([5da49b7](https://github.com/uni-tj/robo-arena/commit/5da49b7b32c69230539e67fb5d7d50149f46b06b)) - [@JulesOxe](https://github.com/JulesOxe)
- main menu + lobby - ([50b5d12](https://github.com/uni-tj/robo-arena/commit/50b5d1257d0cf5bb132fd69c4f647db028829c09)) - [@p-98](https://github.com/p-98)
- game core - ([f33c62d](https://github.com/uni-tj/robo-arena/commit/f33c62d5f719332b036e96123dadb0d2d6acf49d)) - [@p-98](https://github.com/p-98)
#### Miscellaneous Chores
- merge level-generation, gamecore, rendering - ([dc717ef](https://github.com/uni-tj/robo-arena/commit/dc717ef57784e642bd0a447ad5bf078aae5e013e)) - [@p-98](https://github.com/p-98)
- update the structure of the project - ([733097e](https://github.com/uni-tj/robo-arena/commit/733097e7a580dd162c9de65a0c7a42c5568aff4f)) - [@weiserhase](https://github.com/weiserhase)
#### Refactoring
- **(wfc)** comment and refactor wfc - ([a62c1cd](https://github.com/uni-tj/robo-arena/commit/a62c1cdf3cd9a8e4351fd7087ffe5f11a604a091)) - [@weiserhase](https://github.com/weiserhase)

- - -

## [0.3.0](https://github.com/uni-tj/robo-arena/compare/0.2.0..0.3.0) - 2024-05-29
#### Continuous Integration
- silence commit hooks - ([866e792](https://github.com/uni-tj/robo-arena/commit/866e792f20d6e2b7351f2ea166581b6e7d28a03a)) - [@p-98](https://github.com/p-98)
- improve black-flake8 compatability - ([03e4270](https://github.com/uni-tj/robo-arena/commit/03e4270961b63a81246751ee22508fdf8a846a9e)) - [@p-98](https://github.com/p-98)
#### Documentation
- sprintlog 3 - ([2c1cb89](https://github.com/uni-tj/robo-arena/commit/2c1cb8925f6fe9abf33be8d4fc9872d6ca3cd470)) - [@p-98](https://github.com/p-98)

- - -

## [0.2.0](https://github.com/uni-tj/robo-arena/compare/0.1.0..0.2.0) - 2024-05-08
#### Documentation
- fix springlog-2 asset - ([e9bfbdf](https://github.com/uni-tj/robo-arena/commit/e9bfbdf2824440c12f17aa63c31298859c89a15d)) - [@p-98](https://github.com/p-98)
- make CONTRIBUTING.md render as html - ([228e2e1](https://github.com/uni-tj/robo-arena/commit/228e2e1ebc4dbf026b4879b4a45339651b29a09d)) - [@p-98](https://github.com/p-98)
- add sprintlogs to readme - ([8fb1dff](https://github.com/uni-tj/robo-arena/commit/8fb1dff913bbb68779765591138df06607838eba)) - [@p-98](https://github.com/p-98)
- sprintlog 2 - ([1f7f03f](https://github.com/uni-tj/robo-arena/commit/1f7f03f768cd6586b6a7fa74432aa6e2cb245f03)) - [@p-98](https://github.com/p-98)

- - -

## [0.1.0](https://github.com/uni-tj/robo-arena/compare/a8095c927ad5ae1841cd8fafcdb1b321509ed554..0.1.0) - 2024-04-24
#### Bug Fixes
- remove print - ([a2eb4b8](https://github.com/uni-tj/robo-arena/commit/a2eb4b8bc0bbbac1db6a09f1af157dc17a4e8e1f)) - [@weiserhase](https://github.com/weiserhase)
#### Continuous Integration
- fix pages not deploying - ([36ee14f](https://github.com/uni-tj/robo-arena/commit/36ee14f832888018cc72e9d2eca194b680a6cda7)) - [@p-98](https://github.com/p-98)
- fix deploy pages trigger branch - ([fc31472](https://github.com/uni-tj/robo-arena/commit/fc31472f5f8b768ac2338ecf25ed0ca9b3c6fdde)) - [@p-98](https://github.com/p-98)
- add pages workflow - ([cdeafe8](https://github.com/uni-tj/robo-arena/commit/cdeafe84526b9b1beda59d834566aad619b9f09c)) - [@p-98](https://github.com/p-98)
- Fix ci to add Python checks as status checks - ([eaf34cc](https://github.com/uni-tj/robo-arena/commit/eaf34ccf2216dfa6721c7311eb03185df81273cc)) - [@weiserhase](https://github.com/weiserhase)
- stricter flake8 + ci as git hook - ([bfbe811](https://github.com/uni-tj/robo-arena/commit/bfbe81169ab6c4d5082b7150c663f84d706967c9)) - [@p-98](https://github.com/p-98)
- add black formatting check to github workflows - ([6a9cb88](https://github.com/uni-tj/robo-arena/commit/6a9cb88f9103d6eabf3029bc1eddecba58427be7)) - [@weiserhase](https://github.com/weiserhase)
- add python test Workfows - ([6496bab](https://github.com/uni-tj/robo-arena/commit/6496babf96eb29fbb39fb0305c4f2011f5cf73c2)) - [@weiserhase](https://github.com/weiserhase)
- fix cog config - ([819a6c0](https://github.com/uni-tj/robo-arena/commit/819a6c0f447bd902bbb276ea3b3f38258befad57)) - [@p-98](https://github.com/p-98)
- add conventional commits check action - ([f8d5bfe](https://github.com/uni-tj/robo-arena/commit/f8d5bfe75f798b7cbd5d48fbe64a9aee43a00d5f)) - [@weiserhase](https://github.com/weiserhase)
#### Documentation
- created sprintlogfile for first sprint - ([0e5415c](https://github.com/uni-tj/robo-arena/commit/0e5415cb167a42e5abafba39cb8602f0a8cfe9f5)) - [@JulesOxe](https://github.com/JulesOxe)
- add readme with links - ([bf4c60a](https://github.com/uni-tj/robo-arena/commit/bf4c60a75a11e286c68e6fbcc4475d27888b3ddd)) - [@p-98](https://github.com/p-98)
- branch naming convention - ([e49d1cc](https://github.com/uni-tj/robo-arena/commit/e49d1cc760c1c16260c19c6a962778be9f7c470e)) - [@p-98](https://github.com/p-98)
#### Features
- different endings - ([c473018](https://github.com/uni-tj/robo-arena/commit/c4730180d7d3fc9ebc43159c072c2f8295eae784)) - [@p-98](https://github.com/p-98)
- init snake game - ([15c0e29](https://github.com/uni-tj/robo-arena/commit/15c0e2964ff2a42cdaf2bfd87c2a88beea163d0f)) - [@JulesOxe](https://github.com/JulesOxe)
#### Miscellaneous Chores
- fix jules changelog name - ([d9d2fe7](https://github.com/uni-tj/robo-arena/commit/d9d2fe75907c24700f8726e0b817aa35834d3845)) - [@p-98](https://github.com/p-98)
- add python .gitignore to the project - ([17389fd](https://github.com/uni-tj/robo-arena/commit/17389fd5c173055e80924bcf6cf24c08f5b8136e)) - [@weiserhase](https://github.com/weiserhase)
- init cog - ([7dc9ead](https://github.com/uni-tj/robo-arena/commit/7dc9eadf4306d9bc61043ccdf35fa3abeb8dd11f)) - [@p-98](https://github.com/p-98)
- init sprintlog - ([20894ee](https://github.com/uni-tj/robo-arena/commit/20894ee28c662a561024729679e748b828cd0ea1)) - [@p-98](https://github.com/p-98)
- initial commit - ([a8095c9](https://github.com/uni-tj/robo-arena/commit/a8095c927ad5ae1841cd8fafcdb1b321509ed554)) - [@p-98](https://github.com/p-98)
#### Refactoring
- data-types - ([2961731](https://github.com/uni-tj/robo-arena/commit/29617311e7be4422be6e5773acaf069be6c79cb2)) - [@weiserhase](https://github.com/weiserhase)



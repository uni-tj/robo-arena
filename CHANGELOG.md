## [1.1.0](https://github.com/uni-tj/robo-arena/compare/1.0.0..1.1.0) - 2024-09-05
#### Bug Fixes
- **(entity)** no bullet blocking - ([56fbaa7](https://github.com/uni-tj/robo-arena/commit/56fbaa72de65f983f5b13f199ac406449bc7998f)) - [@JulesOxe](https://github.com/JulesOxe)
- **(statistics)** fix unit map - ([78cb6a8](https://github.com/uni-tj/robo-arena/commit/78cb6a87b7a723e4e4cb7c9152cb2c297161c808)) - [@weiserhase](https://github.com/weiserhase)
#### Documentation
- **(readme)** add game start & project structure - ([0ba1190](https://github.com/uni-tj/robo-arena/commit/0ba1190026738b1fb36a88df9f0bcb8d6e3c9627)) - [@p-98](https://github.com/p-98)
- **(spl-7)** Jan - ([85df1e5](https://github.com/uni-tj/robo-arena/commit/85df1e5417821feedb2bc48440af6a5f862677b7)) - [@weiserhase](https://github.com/weiserhase)
- **(sprintlog)** sprintlog-7 - ([0598839](https://github.com/uni-tj/robo-arena/commit/0598839eb934f844450971cb2e287170bab7aa80)) - [@JulesOxe](https://github.com/JulesOxe)
- **(sprintlog-7)** jules content - ([5e40f72](https://github.com/uni-tj/robo-arena/commit/5e40f72e08690381f111ab900561c272a764e870)) - [@JulesOxe](https://github.com/JulesOxe)
#### Features
- **(enemy-ai)** add movement ai - ([4bbbf77](https://github.com/uni-tj/robo-arena/commit/4bbbf779008f2ec95afbbddc863830d05d0369d5)) - [@weiserhase](https://github.com/weiserhase)

- - -

## [1.0.0](https://github.com/uni-tj/robo-arena/compare/0.6.0..1.0.0) - 2024-09-05
#### Bug Fixes
- **(build)** fix pyproject.toml - ([88ed03d](https://github.com/uni-tj/robo-arena/commit/88ed03d3f3029502022de232e1ab5a62767e6008)) - [@weiserhase](https://github.com/weiserhase)
- **(client)** client door events - ([d46e9f6](https://github.com/uni-tj/robo-arena/commit/d46e9f6724cce90a9cbbe70d9636ffc19c5bf43b)) - [@JulesOxe](https://github.com/JulesOxe)
- **(client)** shot event on player - ([9e1ac7b](https://github.com/uni-tj/robo-arena/commit/9e1ac7bc5f7fbd2b78d8eaf4c66d74eff93a67a0)) - [@p-98](https://github.com/p-98)
- **(client)** extrapolation incorrect - ([a3fad69](https://github.com/uni-tj/robo-arena/commit/a3fad69406c7911e14ed928949cd6d56eb1a0e0c)) - [@p-98](https://github.com/p-98)
- **(core)** crash on restart - ([d272c91](https://github.com/uni-tj/robo-arena/commit/d272c91048b1fbfe2b319070514b4d204743fe7d)) - [@p-98](https://github.com/p-98)
- **(flickering-lines)** no more lines visible and background scrolls cleanly and smoothly - ([d79558d](https://github.com/uni-tj/robo-arena/commit/d79558d076865a464d46d10d87a3255b6eb33d95)) - [@JulesOxe](https://github.com/JulesOxe)
- **(level-generation)** Integrate with server/client+ performance improvenments - ([560db2a](https://github.com/uni-tj/robo-arena/commit/560db2a23303c4533ce8a3af3a3548b1564539ab)) - [@weiserhase](https://github.com/weiserhase)
- **(menu)** implement quit - ([7489607](https://github.com/uni-tj/robo-arena/commit/748960770323f86f0806c4e4df1e70232cb39ce4)) - [@p-98](https://github.com/p-98)
- **(movement)** can't move through 1 gu corridors - ([50ad26a](https://github.com/uni-tj/robo-arena/commit/50ad26a8f0ecb781131f6c074cb1f110d6c8546f)) - [@p-98](https://github.com/p-98)
- **(movement)** Move consts + fix normalization - ([41b1eeb](https://github.com/uni-tj/robo-arena/commit/41b1eeb7f0a2bdee2ff47cd15744e6841d88db0f)) - [@weiserhase](https://github.com/weiserhase)
- **(paths)** fix remaining lowercase_path - ([65e108d](https://github.com/uni-tj/robo-arena/commit/65e108da5d4cc253f95b2554fed4c7f6d4f3ae1d)) - [@weiserhase](https://github.com/weiserhase)
- **(player-clips-wall)** player is now overlaid by bottom walls - ([65be4b5](https://github.com/uni-tj/robo-arena/commit/65be4b52e83fc60a05b045e4a0319ccfeb0880e0)) - [@JulesOxe](https://github.com/JulesOxe)
- **(renderer)** debug player blocks check if in fov + perf change colliding blocks - ([c0df09d](https://github.com/uni-tj/robo-arena/commit/c0df09d112014bfac66095a05070a75183eb1573)) - [@weiserhase](https://github.com/weiserhase)
- **(server)** crash when shooting inside enemy - ([372861e](https://github.com/uni-tj/robo-arena/commit/372861e815f5d03a6f730e10ed1bccf70047707c)) - [@p-98](https://github.com/p-98)
- **(server)** crash when bullet moves out of level - ([7d6a162](https://github.com/uni-tj/robo-arena/commit/7d6a1627a320ed889de2c78a8483e001f9c7f004)) - [@p-98](https://github.com/p-98)
- **(sound-is-not-muted)** fade-in-sounds can be muted as well - ([8d2bb82](https://github.com/uni-tj/robo-arena/commit/8d2bb82e4573f10d451e4cb937693547ec765de8)) - [@JulesOxe](https://github.com/JulesOxe)
- **(tileset)** update tilset dep. scaling factor - ([f72f74c](https://github.com/uni-tj/robo-arena/commit/f72f74c9a3e63a98c94a01e06822c1d91a906619)) - [@weiserhase](https://github.com/weiserhase)
- **(timer)** increment run counter - ([9d7399d](https://github.com/uni-tj/robo-arena/commit/9d7399da1378c9398dd8d9000e159baaa846e79b)) - [@weiserhase](https://github.com/weiserhase)
- **(ui)** register listener to events - ([b67a2f5](https://github.com/uni-tj/robo-arena/commit/b67a2f591fce33f8b1bbe6148e3690a429888aa6)) - [@weiserhase](https://github.com/weiserhase)
- **(util)** flake8 missing generic parameter syntax - ([7db04d0](https://github.com/uni-tj/robo-arena/commit/7db04d01f8f48efb4a386f4bc5542f1a4f13dfc2)) - [@p-98](https://github.com/p-98)
- **(waves)** fix the amount of waves per room - ([2f998a4](https://github.com/uni-tj/robo-arena/commit/2f998a49923e07667347c44dcd0e075ab4ef0fcf)) - [@weiserhase](https://github.com/weiserhase)
- entity self-collision - ([92e85ac](https://github.com/uni-tj/robo-arena/commit/92e85ac4c37d5eec3da1d13b7084dddfd01496c6)) - [@p-98](https://github.com/p-98)
- collision markers and better bullet settings - ([215be7b](https://github.com/uni-tj/robo-arena/commit/215be7b6844fc56c0694e805d1d5130a9642e636)) - [@p-98](https://github.com/p-98)
#### Build system
- **(level-generation)** add matplotlib - ([ff48f33](https://github.com/uni-tj/robo-arena/commit/ff48f33b5d77b635f66091952550a101c4b2b7e1)) - [@p-98](https://github.com/p-98)
- switch to python only wheels - ([cd540c8](https://github.com/uni-tj/robo-arena/commit/cd540c8db2ad7c8631cfa6f5e44b42b249149976)) - [@weiserhase](https://github.com/weiserhase)
- Auto build and publich artifacts with new tag - ([6529a35](https://github.com/uni-tj/robo-arena/commit/6529a35f9f45fe44c9281d5fb909f68125a84af5)) - [@weiserhase](https://github.com/weiserhase)
#### Continuous Integration
- **(build)** no build on pr - ([f4f33a8](https://github.com/uni-tj/robo-arena/commit/f4f33a829ea1c6817babb91f18f285091a4cc574)) - [@p-98](https://github.com/p-98)
- **(build)** auto build wheels - ([d22c235](https://github.com/uni-tj/robo-arena/commit/d22c235038f99047b58ca133484a71e7c135dc43)) - [@weiserhase](https://github.com/weiserhase)
- **(build)** add posibility to produce exe - ([4961717](https://github.com/uni-tj/robo-arena/commit/49617177c0d6cc225cf35c86f97f2c4fd086e8df)) - [@weiserhase](https://github.com/weiserhase)
- **(tests)** pytest only tests the test directory - ([b08c1ab](https://github.com/uni-tj/robo-arena/commit/b08c1ab7e3d4e113f56d6b1420f1330119dedffc)) - [@weiserhase](https://github.com/weiserhase)
#### Documentation
- **(utils)** adds comments for shared utils - ([7950740](https://github.com/uni-tj/robo-arena/commit/7950740816c5668400a124d75b8bcf6ccbdd70e1)) - [@weiserhase](https://github.com/weiserhase)
- comment shared/util.py - ([2a3a98a](https://github.com/uni-tj/robo-arena/commit/2a3a98af908b22ecc11012183501ec8fb684d9a8)) - [@p-98](https://github.com/p-98)
- comment shared/types.py - ([737031a](https://github.com/uni-tj/robo-arena/commit/737031a791ead819b6d5506cb9eb29c05be901ba)) - [@p-98](https://github.com/p-98)
- comment shared/time.py - ([571c72b](https://github.com/uni-tj/robo-arena/commit/571c72b5e9c6f00f5dcd91d1293aa281e2496ef5)) - [@p-98](https://github.com/p-98)
- comment shared/network.py - ([8e0b20e](https://github.com/uni-tj/robo-arena/commit/8e0b20ef4474b327a227772b5354dec53cf24997)) - [@p-98](https://github.com/p-98)
- comment shared/game_ui.py - ([63c9a82](https://github.com/uni-tj/robo-arena/commit/63c9a829c31573d8adbfe9ba6b3f3cdcd1bc7428)) - [@p-98](https://github.com/p-98)
- comment shared/entity.py - ([3ff6ed5](https://github.com/uni-tj/robo-arena/commit/3ff6ed5acf96c9cf84735888b2f055c7e309d853)) - [@p-98](https://github.com/p-98)
- comment shared/game.py - ([19f2edf](https://github.com/uni-tj/robo-arena/commit/19f2edf8444bce49ae02e7b43885cf01c2ca38d1)) - [@p-98](https://github.com/p-98)
#### Features
- **(bullet-textures)** design of an alien projectile and a laser projectile - ([02d2494](https://github.com/uni-tj/robo-arena/commit/02d24942f50a7073ba5f4d3bd44ad6f05765eb60)) - [@JulesOxe](https://github.com/JulesOxe)
- **(bullet-textures)** design of an alien projectile and a laser projectile - ([e7ff007](https://github.com/uni-tj/robo-arena/commit/e7ff00727323fc22c6ff5334d45d93bf5fd100d3)) - [@JulesOxe](https://github.com/JulesOxe)
- **(client)** use endscreen - ([45c8f54](https://github.com/uni-tj/robo-arena/commit/45c8f54eb494d08c9792350a1b12d76a603a9892)) - [@p-98](https://github.com/p-98)
- **(client)** enemy shot event - ([99aedf8](https://github.com/uni-tj/robo-arena/commit/99aedf84b69d21a1bba243850bbb2a109a1d1ef5)) - [@p-98](https://github.com/p-98)
- **(client)** client door events - ([a43fe03](https://github.com/uni-tj/robo-arena/commit/a43fe03e72406035262fe50ba58d2b8afebbd586)) - [@p-98](https://github.com/p-98)
- **(client)** forward weapon events to entity - ([52f6ad8](https://github.com/uni-tj/robo-arena/commit/52f6ad8690d0ccefa249d965229ed6cf71517585)) - [@p-98](https://github.com/p-98)
- **(client)** health events - ([1eff752](https://github.com/uni-tj/robo-arena/commit/1eff75212c7e30b45ce96f1ce1432ff416f1d99a)) - [@p-98](https://github.com/p-98)
- **(client)** weapon on client - ([48beeea](https://github.com/uni-tj/robo-arena/commit/48beeea79f31752a92cb93599008e3b09caed430)) - [@p-98](https://github.com/p-98)
- **(client)** player move event - ([9d85e2a](https://github.com/uni-tj/robo-arena/commit/9d85e2ab880e563fd54aeb82d7f1db601e2f1ac5)) - [@p-98](https://github.com/p-98)
- **(constants)** adapt constants for better ux - ([3451ec9](https://github.com/uni-tj/robo-arena/commit/3451ec997ad7221fb118cd96f0adf32e7818e787)) - [@weiserhase](https://github.com/weiserhase)
- **(constants)** adapt weapon constants - ([16269cc](https://github.com/uni-tj/robo-arena/commit/16269cca7fec10fa6801b0c27ebeb5e0e1dbd588)) - [@weiserhase](https://github.com/weiserhase)
- **(core)** restart on player death - ([fe6b68d](https://github.com/uni-tj/robo-arena/commit/fe6b68d3671a4e3978c47971df1201555051c643)) - [@p-98](https://github.com/p-98)
- **(debug)** server/client env on game - ([8ef83d7](https://github.com/uni-tj/robo-arena/commit/8ef83d746d235a6a0b5f500c7b4c17498a21e153)) - [@p-98](https://github.com/p-98)
- **(difficulty)** add dificulty and waves - ([35435df](https://github.com/uni-tj/robo-arena/commit/35435dfe2313a31217dc7dc57848d09d2b574bab)) - [@weiserhase](https://github.com/weiserhase)
- **(door-sounds)** play sounds when doors open/close - ([9c05c6c](https://github.com/uni-tj/robo-arena/commit/9c05c6c19dd628605a92ce4a449f35c511622895)) - [@JulesOxe](https://github.com/JulesOxe)
- **(door-textures)** textures for open and closed doors - ([ac175ec](https://github.com/uni-tj/robo-arena/commit/ac175ec213aec90df8cb47b1385e696d7a6034da)) - [@JulesOxe](https://github.com/JulesOxe)
- **(endscreen)** add endscreen - ([cd10ab6](https://github.com/uni-tj/robo-arena/commit/cd10ab64468447b6e2a4b8e869c3569ce6ac1b88)) - [@JulesOxe](https://github.com/JulesOxe)
- **(enemy-ai)** full working enemyai - ([1a846b1](https://github.com/uni-tj/robo-arena/commit/1a846b1fe963a4fb63ce09cf1f5c42b8d410989e)) - [@weiserhase](https://github.com/weiserhase)
- **(enemy-ai)** add movement ai - ([ed2ee56](https://github.com/uni-tj/robo-arena/commit/ed2ee56b67ab7e95706d448a6f8a158df3080a0a)) - [@weiserhase](https://github.com/weiserhase)
- **(enemy-ai)** add astar + tests + perftests - ([5b2f0b9](https://github.com/uni-tj/robo-arena/commit/5b2f0b97f6c25171fab6a786e58e97f1930fe67a)) - [@weiserhase](https://github.com/weiserhase)
- **(enemy-animation)** add enemy-alien texture and animation - ([e813766](https://github.com/uni-tj/robo-arena/commit/e81376678295b066b6b775ab7422b7f18689f6cd)) - [@JulesOxe](https://github.com/JulesOxe)
- **(enemy-sounds)** base implementation for enemy sounds - ([2cf2dcf](https://github.com/uni-tj/robo-arena/commit/2cf2dcfbc88a4a46c95389ae818928579eb0e5a3)) - [@JulesOxe](https://github.com/JulesOxe)
- **(font)** new font and game titel - ([901fd2a](https://github.com/uni-tj/robo-arena/commit/901fd2adf05730907a1a2b9c7598e1c544f28854)) - [@JulesOxe](https://github.com/JulesOxe)
- **(fps-display)** implementation of fps display - ([4c20a25](https://github.com/uni-tj/robo-arena/commit/4c20a256ef9102b38906e4696b1060affb056f4f)) - [@weiserhase](https://github.com/weiserhase)
- **(game)** colliding_blocks - ([27889b7](https://github.com/uni-tj/robo-arena/commit/27889b7a8d5ccfc71bffa8b5358c83033a675667)) - [@p-98](https://github.com/p-98)
- **(game-ambience-sounds)** base implementation for music and ambience sounds in the game - ([a910fff](https://github.com/uni-tj/robo-arena/commit/a910fff89eff81c6d73c604b632a98a0245628fb)) - [@JulesOxe](https://github.com/JulesOxe)
- **(level-gen)** add obstacles into rooms - ([8c0861a](https://github.com/uni-tj/robo-arena/commit/8c0861a1ca94559c19d9960890a8e024bd523c46)) - [@weiserhase](https://github.com/weiserhase)
- **(level-generation)** random perlin noise - ([d1984e4](https://github.com/uni-tj/robo-arena/commit/d1984e47d686c9e110a4688367915b7ed80f9f89)) - [@JulesOxe](https://github.com/JulesOxe)
- **(level-generation)** consistent player spawn - ([d22be28](https://github.com/uni-tj/robo-arena/commit/d22be2823b6d8185acfbedb25df159b37d3e04dd)) - [@p-98](https://github.com/p-98)
- **(level-generation)** tileset - ([941ef7f](https://github.com/uni-tj/robo-arena/commit/941ef7fc29778fa799bc592764d548805f21623e)) - [@p-98](https://github.com/p-98)
- **(level-generation)** tileset from edges - ([ffdcbf8](https://github.com/uni-tj/robo-arena/commit/ffdcbf89d7afab264e3d17c1d88b655b126e15c2)) - [@p-98](https://github.com/p-98)
- **(menu)** score - ([8242eee](https://github.com/uni-tj/robo-arena/commit/8242eee15b02081f4fa0177cc7185084c45e6fe2)) - [@p-98](https://github.com/p-98)
- **(menue-sounds)** base implementation for music and sound in the menues - ([c6de61a](https://github.com/uni-tj/robo-arena/commit/c6de61abf85fca726860ba56201a1a6b049091d3)) - [@JulesOxe](https://github.com/JulesOxe)
- **(movement)** move along wall - ([7381eec](https://github.com/uni-tj/robo-arena/commit/7381eec92ea2bff80696ebb37276f2fc4afa271a)) - [@p-98](https://github.com/p-98)
- **(perlin)** add perlin noise generation - ([b1e7097](https://github.com/uni-tj/robo-arena/commit/b1e7097d4a36baab6fe6f4500d2c113a1a22b523)) - [@weiserhase](https://github.com/weiserhase)
- **(player-animation)** add player-robot graphic an animation - ([7d41b38](https://github.com/uni-tj/robo-arena/commit/7d41b38df3a03b18db0d86f362dada01c26cbae6)) - [@JulesOxe](https://github.com/JulesOxe)
- **(player-sounds)** base implementation for player sounds - ([42170ae](https://github.com/uni-tj/robo-arena/commit/42170ae4bd32527d9d790b24b84c5139a4b1822f)) - [@JulesOxe](https://github.com/JulesOxe)
- **(render)** weapons - ([5ceec7b](https://github.com/uni-tj/robo-arena/commit/5ceec7b23f521af8d9f0a59cce74a26716674bb2)) - [@p-98](https://github.com/p-98)
- **(render)** use door textures - ([627c4bf](https://github.com/uni-tj/robo-arena/commit/627c4bf35e966011a062a3d13b50ba36c99d1112)) - [@p-98](https://github.com/p-98)
- **(render)** precise clock - ([1dd3567](https://github.com/uni-tj/robo-arena/commit/1dd35677524d4e0b320e7a3be5682b8b6ef53e9f)) - [@p-98](https://github.com/p-98)
- **(render)** use bullet texture - ([fedffe9](https://github.com/uni-tj/robo-arena/commit/fedffe95337e60a6ea538b90308ffa36846684b2)) - [@p-98](https://github.com/p-98)
- **(rooms)** door open/close events - ([25e043a](https://github.com/uni-tj/robo-arena/commit/25e043a47e8c41905f6047fc6a369fb93a999520)) - [@p-98](https://github.com/p-98)
- **(rooms)** add rooms - ([e656c6f](https://github.com/uni-tj/robo-arena/commit/e656c6fe2b3236fe82ae0c78d57ce06724ef1a52)) - [@p-98](https://github.com/p-98)
- **(server)** heal player after room end - ([55ad42b](https://github.com/uni-tj/robo-arena/commit/55ad42bcffb67be8e0a1e96dfab87c34a2e278d9)) - [@p-98](https://github.com/p-98)
- **(server)** death event on enemy - ([cca29b2](https://github.com/uni-tj/robo-arena/commit/cca29b22850ecc256db7fc671513296cfcfe81a0)) - [@p-98](https://github.com/p-98)
- **(smooth-camera-movement)** replace pos-Buffer - ([aa30a90](https://github.com/uni-tj/robo-arena/commit/aa30a90c708a9d94c611b909c8ea99fd7e306eef)) - [@weiserhase](https://github.com/weiserhase)
- **(smooth-movement)** base implementation of the smooth-palyer-movement feature - ([3597f55](https://github.com/uni-tj/robo-arena/commit/3597f55078c26111d7ae73256a67fb4627fce73a)) - [@JulesOxe](https://github.com/JulesOxe)
- **(smooth-movement)** base implementation of the smooth-palyer-movement feature - ([829ce9b](https://github.com/uni-tj/robo-arena/commit/829ce9b58b234250152a4e110de258027a17998c)) - [@JulesOxe](https://github.com/JulesOxe)
- **(timer)** add periodic-printing+console clearing - ([c43dad0](https://github.com/uni-tj/robo-arena/commit/c43dad047cb898c807d9b7f2f64797ab550836a9)) - [@weiserhase](https://github.com/weiserhase)
- **(ui)** link healthbar to player - ([5f8487e](https://github.com/uni-tj/robo-arena/commit/5f8487ec324787886d3e443670ce98fc22ef7dbd)) - [@JulesOxe](https://github.com/JulesOxe)
- **(util)** throttle - ([24a876c](https://github.com/uni-tj/robo-arena/commit/24a876cd39d556e5b3b0bf216193d4306db95711)) - [@p-98](https://github.com/p-98)
- **(util)** search_connected & neighbours_4 - ([d62e4a3](https://github.com/uni-tj/robo-arena/commit/d62e4a377d29afdbd6f2c3b5910dd0477bc59b08)) - [@weiserhase](https://github.com/weiserhase)
- **(utils)** add Matrix2d - ([dc7be0d](https://github.com/uni-tj/robo-arena/commit/dc7be0dd7dd35889bcdecc0ada208637182fcf6b)) - [@weiserhase](https://github.com/weiserhase)
- **(void-texture)** texture for void block - ([52a1344](https://github.com/uni-tj/robo-arena/commit/52a13445b1b8e8870f44f8812bda1f65c0168e0c)) - [@JulesOxe](https://github.com/JulesOxe)
- **(wfc-rewrite)** performance + quality improvements + bug fixes - ([97812d0](https://github.com/uni-tj/robo-arena/commit/97812d09dbbac7a3489bbd962e95e03f4b9e79ac)) - [@weiserhase](https://github.com/weiserhase)
- **(wfc-rewrite)** Rewrite of the wfc for better performance - ([1d8b782](https://github.com/uni-tj/robo-arena/commit/1d8b782d086e45d09e65defab485812bcedf247d)) - [@weiserhase](https://github.com/weiserhase)
- enemy bullets - ([784a0fb](https://github.com/uni-tj/robo-arena/commit/784a0fbde543dc49d966734cd28f981459450fd1)) - [@p-98](https://github.com/p-98)
- door entity - ([a728004](https://github.com/uni-tj/robo-arena/commit/a7280048928a2b86f343483f5ba4d42c88534962)) - [@p-98](https://github.com/p-98)
- `StartFrameEvent` on game & frame_cache - ([569f131](https://github.com/uni-tj/robo-arena/commit/569f1314940dfe02aa335b9106a2a5fea2de87bb)) - [@p-98](https://github.com/p-98)
- player wall collision - ([8878e11](https://github.com/uni-tj/robo-arena/commit/8878e1142894e58d119222c26d05db6ccbaf8ebe)) - [@p-98](https://github.com/p-98)
- debugging markers - ([43a49a4](https://github.com/uni-tj/robo-arena/commit/43a49a4c18b002cda6ac999ada4ee3db64d7112a)) - [@p-98](https://github.com/p-98)
- weapon + bullet + health + collisions - ([ed06e53](https://github.com/uni-tj/robo-arena/commit/ed06e53d4786e85423fe4cf84a908cddb71b9af5)) - [@p-98](https://github.com/p-98)
- base implementation of the menu feature - ([2bd6e7c](https://github.com/uni-tj/robo-arena/commit/2bd6e7c572886a8993c4fac62b8db49a41fb3960)) - [@JulesOxe](https://github.com/JulesOxe)
- designed first basic game graphics - ([ee6a7b6](https://github.com/uni-tj/robo-arena/commit/ee6a7b669bf45dd6e71ecdd280d9b248cd78edfe)) - [@JulesOxe](https://github.com/JulesOxe)
#### Miscellaneous Chores
- **(wfc-rewrite)** clean up old wfc code - ([e76a445](https://github.com/uni-tj/robo-arena/commit/e76a445118f1223c04297d313a50d37cb4dd7346)) - [@weiserhase](https://github.com/weiserhase)
#### Performance Improvements
- **(enemy-ai)** revert remove value interpolation - ([475c1d8](https://github.com/uni-tj/robo-arena/commit/475c1d81b8d7186bdb62d497f25b55315072b2fc)) - [@JulesOxe](https://github.com/JulesOxe)
- **(enemy-ai)** remove value interpolation - ([5d57317](https://github.com/uni-tj/robo-arena/commit/5d573175bbc04e7940e12570fa3daffcd14d60e3)) - [@weiserhase](https://github.com/weiserhase)
- **(level-generation)** multiple perf improvement - ([b071959](https://github.com/uni-tj/robo-arena/commit/b0719593a54fb73810ee48d27cccbf4278a894ab)) - [@weiserhase](https://github.com/weiserhase)
- **(level-generation)** perf-testing + wf helpers - ([6a69002](https://github.com/uni-tj/robo-arena/commit/6a690020438465529e29c9e75087fe937c9ee947)) - [@weiserhase](https://github.com/weiserhase)
- **(level-generation)** entropy store + arg dedupe - ([532adf8](https://github.com/uni-tj/robo-arena/commit/532adf8ed9942d9cd5e65163b4528beed906542c)) - [@weiserhase](https://github.com/weiserhase)
- **(renderer)** improve perrformance in renderer - ([5eb1f61](https://github.com/uni-tj/robo-arena/commit/5eb1f6119e36fdec59988b22b00874ff87401d97)) - [@weiserhase](https://github.com/weiserhase)
- **(renderer)** multiple performance improvements - ([4a9e6bd](https://github.com/uni-tj/robo-arena/commit/4a9e6bdf46e0302aa6d6c690b4fc23c66b722fa3)) - [@weiserhase](https://github.com/weiserhase)
- **(server)** remove seperate receiver thread - ([24f8671](https://github.com/uni-tj/robo-arena/commit/24f86710fd3bc5a43743663409bd01c2df804ce8)) - [@p-98](https://github.com/p-98)
- **(util)** fix frame_cache spikes - ([3f5f608](https://github.com/uni-tj/robo-arena/commit/3f5f6082d5ba7a446a8bd6f51d0d013b04ba343d)) - [@p-98](https://github.com/p-98)
#### Refactoring
- **(client)** remove legacy render aim - ([9af365f](https://github.com/uni-tj/robo-arena/commit/9af365feca91bfbd47ffe139a1f20ad4cd6ec7eb)) - [@p-98](https://github.com/p-98)
- **(constants)** types & constants cleanup - ([85bfdcb](https://github.com/uni-tj/robo-arena/commit/85bfdcb00fc7136fea3bda54d425b0a4152f1119)) - [@JulesOxe](https://github.com/JulesOxe)
- **(constants)** server - ([483afe5](https://github.com/uni-tj/robo-arena/commit/483afe5b7f442230ff9a683e27e08c082aa0518a)) - [@JulesOxe](https://github.com/JulesOxe)
- **(constants)** shared - ([44e80c9](https://github.com/uni-tj/robo-arena/commit/44e80c92b9361fa82fc05523f5462f7077c9b0b3)) - [@JulesOxe](https://github.com/JulesOxe)
- **(constants)** client - ([55c59fa](https://github.com/uni-tj/robo-arena/commit/55c59faef50ecf9de911784c7ab7c27fe9e5dd01)) - [@JulesOxe](https://github.com/JulesOxe)
- **(constants)** menu - ([c97e2ed](https://github.com/uni-tj/robo-arena/commit/c97e2ed77a29904d5cc05b94383028aa3045e942)) - [@JulesOxe](https://github.com/JulesOxe)
- **(level-generation)** fine tune constants - ([5c25108](https://github.com/uni-tj/robo-arena/commit/5c25108691417852a768212acb14b47c5fe1a70f)) - [@p-98](https://github.com/p-98)
- **(level-generation)** remove unused comment - ([d951a23](https://github.com/uni-tj/robo-arena/commit/d951a23d487d173e47223f22a67d2756f684308a)) - [@p-98](https://github.com/p-98)
- **(level-generation)** rewrite wfc - ([1ee9346](https://github.com/uni-tj/robo-arena/commit/1ee9346abd4b34beb85ac1a28c17075ad9755a91)) - [@p-98](https://github.com/p-98)
- **(menu)** remove unnecessary close alias - ([a07d9c9](https://github.com/uni-tj/robo-arena/commit/a07d9c9a2d422cf2d748803d1788be3c1559294b)) - [@p-98](https://github.com/p-98)
- **(menus)** duplicated code removed - ([e122ea1](https://github.com/uni-tj/robo-arena/commit/e122ea1f36f7238ebcc77ff4eb190ad7340bf8d4)) - [@JulesOxe](https://github.com/JulesOxe)
- **(rename)** rename files to lowercase - ([2369f59](https://github.com/uni-tj/robo-arena/commit/2369f5969e31513d15d05b19a6e7234054e2f98c)) - [@weiserhase](https://github.com/weiserhase)
- **(render)** adapt graphic scale constants - ([28481ae](https://github.com/uni-tj/robo-arena/commit/28481ae3aa09ffbbdc368053515f60edec4f952f)) - [@p-98](https://github.com/p-98)
- **(render)** renames and render_above_player - ([392047f](https://github.com/uni-tj/robo-arena/commit/392047f8820a08ed39f035fdaae66d66df21614d)) - [@p-98](https://github.com/p-98)
- **(rooms)** fine tune obstacles - ([7073908](https://github.com/uni-tj/robo-arena/commit/7073908df724e82e9e335686351651d288ef2467)) - [@p-98](https://github.com/p-98)
- **(rooms)** decrease enemy shooting speed - ([b68ee4b](https://github.com/uni-tj/robo-arena/commit/b68ee4b4649b5352a3f77bd496c04efc7240511a)) - [@p-98](https://github.com/p-98)
- **(smooth-camera-movement)** cleanup code - ([233ca04](https://github.com/uni-tj/robo-arena/commit/233ca041b4807756980466ca756cb4377334c223)) - [@p-98](https://github.com/p-98)
- **(smooth-camera-movement)** create class for camera-movement - ([d396e75](https://github.com/uni-tj/robo-arena/commit/d396e7578b876661c76b00857c8c5a25159544f8)) - [@JulesOxe](https://github.com/JulesOxe)
- **(sound)** cleanup ambient sounds - ([1433d6e](https://github.com/uni-tj/robo-arena/commit/1433d6ed7600d09accd297ecbe2a75a49e10af48)) - [@p-98](https://github.com/p-98)
- **(sounds)** sound leveling - ([08c1c99](https://github.com/uni-tj/robo-arena/commit/08c1c99f84ef47bf30a97be7824b142a04d61ed2)) - [@JulesOxe](https://github.com/JulesOxe)
- **(textures)** add & adapt unscaled textures - ([05b8da3](https://github.com/uni-tj/robo-arena/commit/05b8da332c6d2eb6c2e6d661194f5b1ddf91f6de)) - [@JulesOxe](https://github.com/JulesOxe)
- **(utils)** move perftester to utils + split progress bar from perftester - ([cd7d9b4](https://github.com/uni-tj/robo-arena/commit/cd7d9b45459356e3985e9465c9975c209be761e7)) - [@weiserhase](https://github.com/weiserhase)
- **(vector)** refactor file and type names - ([8717455](https://github.com/uni-tj/robo-arena/commit/8717455d80d3b1e73adb5c8ccd4d521c2c538698)) - [@weiserhase](https://github.com/weiserhase)
- **(wfc)** unique blocks & simplify level conv - ([c820d28](https://github.com/uni-tj/robo-arena/commit/c820d28d967acffbbebf6f7569808099667acf02)) - [@p-98](https://github.com/p-98)
- remove debug renders & cleanup - ([d912e75](https://github.com/uni-tj/robo-arena/commit/d912e758e31396172c755865d9cd3f6c40ead912)) - [@JulesOxe](https://github.com/JulesOxe)
- cleanup shared/game.py - ([62c0538](https://github.com/uni-tj/robo-arena/commit/62c05385ff659169a7bf024facff322902429c51)) - [@p-98](https://github.com/p-98)
- comment & cleanup shared/block.py - ([9073507](https://github.com/uni-tj/robo-arena/commit/90735078d4a677c75eac4f862b1d5618c1bebfe1)) - [@p-98](https://github.com/p-98)
- fix rebase problems - ([b8db149](https://github.com/uni-tj/robo-arena/commit/b8db14993c2d48ac73b1ea69eb8f365ce61544b6)) - [@weiserhase](https://github.com/weiserhase)
- collision by blocks_robot, blocks_bullet - ([c3cce19](https://github.com/uni-tj/robo-arena/commit/c3cce199fc1f71c94aafd737eff0f8f5b5f95cdd)) - [@p-98](https://github.com/p-98)
- add change_exception - ([fa440a2](https://github.com/uni-tj/robo-arena/commit/fa440a2f585a94429c5c84c0e4ae68fcf5bbe03e)) - [@p-98](https://github.com/p-98)
- remove block inheritance - ([67857dc](https://github.com/uni-tj/robo-arena/commit/67857dcc2934af552e05bea31631b3bc498ed4cb)) - [@p-98](https://github.com/p-98)
#### Tests
- **(frame-cache)** test frame cache performance - ([1bb457b](https://github.com/uni-tj/robo-arena/commit/1bb457ba0a30bf75788da1410562a3dea755bc17)) - [@weiserhase](https://github.com/weiserhase)
- **(timer)** add timer for intra function timings - ([197c9fc](https://github.com/uni-tj/robo-arena/commit/197c9fc791146afa38e462109a6fcea5b2bc0ef5)) - [@weiserhase](https://github.com/weiserhase)
- **(vector)** Vector and Tuple Vector Test - ([3c6a96d](https://github.com/uni-tj/robo-arena/commit/3c6a96d77d558aa7cced87b673db5dc035fdf623)) - [@weiserhase](https://github.com/weiserhase)

- - -

## [0.6.0](https://github.com/uni-tj/robo-arena/compare/0.5.0..0.6.0) - 2024-07-10
#### Bug Fixes
- **(rendering)** move cache clear to ctx creation - ([efee37e](https://github.com/uni-tj/robo-arena/commit/efee37e6a3c1bcd812f782e7d566e7979f2ff28e)) - [@p-98](https://github.com/p-98)
#### Documentation
- sprintlog 6 - ([44a8671](https://github.com/uni-tj/robo-arena/commit/44a86719a53bd222220c5a311592be70e836d60b)) - [@p-98](https://github.com/p-98)
#### Features
- **(client)** track mouse position - ([48aa81c](https://github.com/uni-tj/robo-arena/commit/48aa81ce0614aa9ffd97a30ab7c5f0357198bd8a)) - [@p-98](https://github.com/p-98)
- quit gracefully - ([b41de52](https://github.com/uni-tj/robo-arena/commit/b41de5248e113c2fd58e282d29679efd89b89ead)) - [@p-98](https://github.com/p-98)
#### Miscellaneous Chores
- **(version)** 0.1.0 - 0.5.0 - ([7b4c40d](https://github.com/uni-tj/robo-arena/commit/7b4c40d2ce9fe32574476c8e6afc31ac16b93b28)) - [@p-98](https://github.com/p-98)
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



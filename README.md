# H7CTF 2025 Finals

Challenges and source for the H7CTF 2025 Finals. H7CTF is an international CTF run by Abu and team H7Tex at SRMIST.

## Challenges

| Category | Challenge | Folder | Author |
| --- | --- | --- | --- |
| AI | AI Guardian | `ai/guardian` | Solvz |
| Blockchain | Token Overflow | `blockchain/overflow` | AbuCTF |
| Blockchain | Escrow Bypass | `blockchain/escrow` | AbuCTF |
| Boot2Root | CPR | `boot2root/cpr` | AbuCTF |
| Crypto | Coffee Would Be Nice | `crypto/coffee` | Solvz |
| Misc | Insanity Check | `misc/insanity` | Abu |
| Pwn | jail-jail | `pwn/jail` | Abu |
| Pwn | K980 | `pwn/k980` | Abu |
| Web | SecureHR | `web/securehr` | N1sh |
| Web | SecureAuth | `web/secureauth` | N1sh |
| Web | Todo | `web/todo` | N1sh |
| Web | RelayGrid | `web/relaygrid` | PsychoSherlock |
| Web | Fetch The Flag | `web/fetch` | PsychoSherlock |

## Layout

Each challenge folder has a `README.md` with the description, how to run it and the solution. The rest is the source as it was deployed: a `Dockerfile` or `docker-compose.yml` for hosted challenges, a `Vagrantfile` for the boot2root box, the handout zip for pwn, and `solve.py` / `solve/` where there is a solver.

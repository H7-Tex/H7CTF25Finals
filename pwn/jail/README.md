# jail-jail

**Category:** Pwn  **Author:** Abu

Handout: `jail-jail.zip`. Deploy: `cd chall && docker compose up --build` (port 1337).

## Solution

The binary is tiny. `main` mmaps a 0x1000 page, reads up to 0x1000 bytes of shellcode into it, flips it to `r-x`, calls `install_seccomp()` and jumps to the page. The seccomp filter only allows `read`, `write`, `open`, `mprotect`, `lseek` and `exit`. No `execve`, no `getdents`, and the flag file has a random name, so open-read-write on a guessed path is out.

The trick is that the service is `socat ... fork`. Every connection is its own process, running as the same user, and a second connection sits blocked in `read()` *before* it ever installs the filter. If I can write into that process I can patch `install_seccomp` itself.

`/proc/<pid>/mem` lets you do exactly that, and seccomp doesn't care because it's just `open` + `lseek` + `write`. So the plan:

1. Open two connections, `io` and `shell`. The second one is the victim.
2. On `io`, `mprotect` my own page back to RWX so I can keep loading stages, then read `/proc/sys/kernel/ns_last_pid`. The last PID handed out is the victim's.
3. Read `/proc/<pid>/maps` to get the victim's PIE base.
4. Open `/proc/<pid>/mem` read-write, `lseek` to `base + 0x1209` (`install_seccomp`) and write `shellcraft.sh()` over it.
5. Send anything on `shell`. Its `read()` returns, it "installs seccomp", which is now a shell.

Each stage ends with a small `read(0, rip+0xc, 0x1000)` stub so the next stage gets read in right after the current code and runs. `chall/exploit.py` is the full script (the host/port in it are the ones from the event).

```
$ python3 chall/exploit.py
$ cat /tmp/flag-*
```

Flag: `H7CTF{pwn_4_d4y_keeps_4_d0ct0r_aw4y_<uuid>}` (UUID generated per container)

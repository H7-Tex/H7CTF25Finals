# K980

**Category:** Pwn  **Author:** Abu

Handout: `K980.zip` (binary, `libc.so.6`, `ld-2.35.so`). Deploy: `cd chall && docker build -t k980 . && docker run -p 1337:1337 k980`

## Solution

Standard note menu: create, edit, read, delete, with 16 slots. The pointer table lives at `0x4040c0` and the sizes at `0x404040`. The binary has no PIE, but it is Full RELRO, so the GOT is not an option. There's a `backdoor` function at `0x401550` that calls `system("/bin/sh")`, so all I need is control of RIP.

Two things stand out in `main`:

- `create` refuses any size `<= 0x4ff`. Every chunk is too big for tcache and fastbins, so you are working with the unsorted and large bins on glibc 2.35.
- `delete` frees the pointer and never clears the slot. `read` and `edit` still work on freed chunks, so it's a plain use-after-free.

How I'd go through it:

1. Allocate two chunks plus a guard, free the first one and `read` it. Its fd/bk point into `main_arena`, which gives the libc base.
2. Use the UAF to get a write primitive. Since the table is at a fixed address, unsafe unlink against `0x4040c0` works well: overlap two freed chunks so one slot points into the middle of another live chunk, fake a free chunk whose `fd`/`bk` are `&table[i]-0x18` / `&table[i]-0x10`, clear `PREV_INUSE` on the next header and free it. The slot then points at the table itself, and `edit` on it rewrites the table. (A largebin attack also works if you prefer that route.)
3. With arbitrary read/write, read `environ` from libc to get a stack address. Then point a slot at the saved return address of `read_input` and `edit` it with `backdoor`, adding a `ret` first if `system` complains about stack alignment.

The flag is written to `/tmp/flag-<uuid>.txt` at startup:

```
$ cat /tmp/flag-*
```

Flag: `H7CTF{y0u_h34p_wh4t_y0u_s0w_<uuid>` (UUID generated per container; note the entrypoint leaves off the closing brace)

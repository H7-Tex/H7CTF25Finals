# Insanity Check

**Category:** Misc  **Difficulty:** Easy  **Author:** Abu

> Seven horcruxes scattered across the Discord server.
>
> Find them. Destroy them. Pass through the platform.
>
> Order irrelevant. Completion mandatory.

Run: `./build.sh`, then `docker run -p 3000:3000 platform-nine-three-quarters`

## Solution

This one is a Discord scavenger hunt. Seven flags were hidden around the H7CTF server: announcements, pinned messages, threads, channel names, bot output and so on. The web app ("Platform 9¾") only accepts them; it never shows them. It stores SHA-256 hashes of the seven, so reading the frontend gets you nothing.

Hints:

1. Start where announcements live. End where nobody looks.
2. Pins, threads, channels, bots. Search everywhere. Click everything.
3. Some flags are in messages. Some are in names. Some are in places you've already been.

The seven horcruxes:

```
H7CTF{c4ll_0ut_my_name}
H7CTF{always_check_the_discord_start_messages_of_a_ctf_i_have_seen_it_a_number_of_times}
H7CTF{h1d1ng_fl4gs_1n_d1sc0rd_1s_cr4zy}
H7CTF{never_gonna_give_you_up_never_gonna_let_you_down}
H7CTF{keeping_this_small_to_make_life_easier}
H7CTF{do_you_believe_in_love_at_first_sight}
H7CTF{https://pbs.twimg.com/media/F43XxNAb0AAugH3?format=jpg&name=small}
```

Submit them in any order. Progress is tracked per session ID (kept in localStorage). Once all seven are in, `/api/final` hands out the real flag. `solve.sh` does the whole thing against a local instance.

Flag: `H7CTF{dumbled0re_w0uld_b3_very_pr0ud_<uuid>}` (UUID generated per container)

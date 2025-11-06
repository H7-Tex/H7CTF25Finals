# CTFd Challenge Description

## Challenge Name
**Insanity Check**

## Category
Miscellaneous (MISC) / OSINT

## Difficulty
Easy

## Points
100 (or adjust based on your scoring system)

## Description

```
Seven horcruxes scattered across the Discord server.

Find them. Destroy them. Pass through the platform.

Order irrelevant. Completion mandatory.

Challenge URL: [DEPLOYMENT_URL]
```

## Hints (Optional - Release after X hours)

**Hint 1 (Free/50 points):**
```
Start where announcements live. End where nobody looks.
```

**Hint 2 (100 points):**
```
Pins, threads, channels, bots. Search everywhere. Click everything.
```

**Hint 3 (150 points):**
```
Some flags are in messages. Some are in names. Some are in places you've already been.
```

## Solution Overview (For Organizers)

The seven flags participants need to find in Discord:
1. `H7CTF{c4ll_0ut_my_name}`
2. `H7CTF{always_check_the_discord_start_messages_of_a_ctf_i_have_seen_it_a_number_of_times}`
3. `H7CTF{h1d1ng_fl4gs_1n_d1sc0rd_1s_cr4zy}`
4. `H7CTF{never_gonna_give_you_up_never_gonna_let_you_down}`
5. `H7CTF{keeping_this_small_to_make_life_easier}`
6. `H7CTF{do_you_believe_in_love_at_first_sight}`
7. `H7CTF{https://pbs.twimg.com/media/F43XxNAb0AAugH3?format=jpg&name=small}`

Once all 7 flags are submitted to the webapp, the final flag is revealed:
`H7CTF{dumbled0re_w0uld_b3_very_pr0ud_{UUID}}`

The final flag contains a unique UUID generated per Docker container instance.

## Deployment Instructions

```bash
cd misc/abu_misc_1
docker build -t platform-nine-three-quarters .
docker run -d -p 3000:3000 --name platform934 platform-nine-three-quarters
```

Access at: `http://your-server:3000`

## Flag Format
`H7CTF{dumbled0re_w0uld_b3_very_pr0ud_[UUID]}`

Example: `H7CTF{dumbled0re_w0uld_b3_very_pr0ud_a1b2c3d4-e5f6-7890-abcd-ef1234567890}`

## Tags
`misc`, `osint`, `discord`, `scavenger-hunt`, `easy`

## Educational Value
- Teaches participants to thoroughly explore communication platforms
- Encourages attention to detail in CTF communications
- Reinforces the importance of reading announcements and rules
- Simulates real-world OSINT scenarios where information is scattered

## Author
AbuCTF

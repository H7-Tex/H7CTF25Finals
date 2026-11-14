# RelayGrid

**Category:** Web  **Author:** PsychoSherlock

Run: `docker build -t relaygrid . && docker run -p 5000:5000 relaygrid`

## Solution

RelayGrid is a small webmail. You can sign up, send mail to other `@relaymailgrid.com` users, set a recovery email, and request a password reset. Every form has an image CAPTCHA.

The flag is in a mail that `relaymailgrid@relaymailgrid.com` sent to `admin@relaymailgrid.com` at startup. The admin account has no recovery email, so it can't be reset. The relay account can, and its recovery email is the admin. `/email/<id>` lets you read a mail if you're the receiver *or the sender*, so owning the relay account is enough.

Reset links look like `/recoveryForm?token=<uuid>`. The tokens are UUIDv1: the clock sequence and node are fixed for the process, and only the timestamp moves, by a random 1000-2000 ticks per token. If you sandwich the relay account's token between two of your own, you've basically got it:

1. Sign up two accounts, `a` and `b`. Set `a`'s recovery email to `b` so `a`'s reset links show up in `b`'s inbox.
2. Request a reset for `a`, then for `relaymailgrid`, then for `a` again, back to back.
3. Read the two links in `b`'s inbox. The relay token has the same node and clock sequence, and its timestamp is strictly between yours, at most ~2000 values to try.

The CAPTCHA looks like it should stop the brute force, but it lives in Flask's client-side session cookie. Solve one, keep that cookie and `captcha_token`, and replay them on every request; the server only removes the CAPTCHA from the *new* cookie it hands back. Single gunicorn worker, so the counter is shared and the window stays tight.

Spray `POST /recoveryForm?token=<candidate>` with a new password until the response redirects to `/login`, log in as `relaymailgrid@relaymailgrid.com`, and open the first mail:

```
GET /email/1
```

Tokens expire after 30 minutes, so do the requests and the spray in one go.

Flag: `H7CTF{r4nd0m_UU1DV3rsi0n1_15_d4mn_vu1nerabl3_<uuid>}` (UUID generated per container)

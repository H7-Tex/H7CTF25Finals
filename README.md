`H7CTF 2025 Finals`

- **ai**
  - [AI Guardian](ai/guardian) `Solvz`
- **blockchain**
  - [Token Overflow](blockchain/overflow) `Abu`, [Escrow Bypass](blockchain/escrow) `Abu`
- **boot2root**
  - [CPR](boot2root/cpr) `Abu`
- **crypto**
  - [Coffee Would Be Nice](crypto/coffee) `Solvz`
- **misc**
  - [Insanity Check](misc/insanity) `Abu`
- **pwn**
  - [jail-jail](pwn/jail) `Abu`, [K980](pwn/k980) `Abu`
- **web**
  - [SecureHR](web/securehr) `N1sh`, [SecureAuth](web/secureauth) `N1sh`, [Todo](web/todo) `N1sh`, [RelayGrid](web/relaygrid) `PsychoSherlock`, [Fetch The Flag](web/fetch) `PsychoSherlock`

each challenge is `<category>/<slug>/` with a `README.md` (description, how to run it, solution) next to the source we deployed, the handout and a solve where we had one

remote ones have a `Dockerfile` or `docker-compose.yml` at the top, so spinning one up is just

```
cd crypto/coffee && docker compose up
```

`boot2root/cpr` is a Vagrant box (`Vagrantfile`), not Docker

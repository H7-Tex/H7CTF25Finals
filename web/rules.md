instruction for authors:

create a new directory in the format `<category>_<author-name>_<serial-number>`

example: `pwn_abu_1`

if it's a challenge requiring instance, have a simple script referenced in the Dockerfile.
it can be a simple `docker-entrypoint.sh`

with the flag generator as follows:
```
FLAG="H7CTF{<static-part>_$(uuidgen)}"
```
test your build locally and push to gh.

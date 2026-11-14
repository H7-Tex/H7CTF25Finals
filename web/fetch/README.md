# Fetch The Flag

**Category:** Web  **Author:** PsychoSherlock

Run: `docker build -t web_ps2 . && docker run -p 3000:3000 web_ps2`

## Solution

The page is a Next.js app with one big button. Clicking it shows `H7CTF{F4K3_FL4G_N1C3_TRY_D1DDY}`. In the network tab the button sends `POST /api/flag` with `{"data":"<base64 blob>"}` and gets another blob back, which the client decodes. The client bundle is run through javascript-obfuscator and source maps are stripped, so reading it takes some patience.

What the client actually sends is `{"fakeFlag":true}`, "encrypted" with a homemade scheme:

1. XOR with a 128-char hex key (as a string)
2. add 13 to every byte, mod 256
3. XOR with a 64-char hex IV string
4. reverse the string, then base64

Both constants sit in the bundle. The API returns the real flag for anything where `fakeFlag !== true`. The fastest way is to put a breakpoint on the encrypt call in DevTools and change `fakeFlag` to `false` before it runs. Or reimplement it:

```python
import base64, json, requests

K = "d124f56bcbf01e6c9ed55be74df1fe5cac01adf9daacd5629cfa7ee3e1490247499e7a2af6b11ac5524f6b11759ebd90a7782c77ab183ee14b710dd8f5ac78fa"
IV = "64a4a0bb067e2848f082da7026da5341905ed4b80b2599c025a04fcb2b9adb59"
x = lambda s, k: "".join(chr(ord(c) ^ ord(k[i % len(k)])) for i, c in enumerate(s))
sh = lambda s, n: "".join(chr((ord(c) + n) % 256) for c in s)

def enc(o):
    return base64.b64encode(x(sh(x(json.dumps(o), K), 13), IV)[::-1].encode("latin1")).decode()

def dec(d):
    return json.loads(x(sh(x(base64.b64decode(d).decode("latin1")[::-1], IV), -13), K))

r = requests.post("http://localhost:3000/api/flag", json={"data": enc({"fakeFlag": False})})
print(dec(r.json()["data"]))
```

Flag: `H7CTF{b4uh_y0u_br0k3_th3_c0d3_0r_th3_c0de_br0ke_y0u_<uuid>}` (UUID generated per container)

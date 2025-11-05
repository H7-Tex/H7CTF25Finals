const _0x1111 = [
  "charCodeAt",
  "fromCharCode",
  "length",
  "floor",
  "random",
  "stringify",
  "parse",
] as const;
const _0x2222 =
  "d124f56bcbf01e6c9ed55be74df1fe5cac01adf9daacd5629cfa7ee3e1490247499e7a2af6b11ac5524f6b11759ebd90a7782c77ab183ee14b710dd8f5ac78fa";
const _0x3333 =
  "64a4a0bb067e2848f082da7026da5341905ed4b80b2599c025a04fcb2b9adb59";

function _0xa7c2(a: string, b: string): string {
  let r = "";
  for (let i = 0; i < (a as any)[_0x1111[2]]; i++) {
    r += (String as any)[_0x1111[1]](
      (a as any)[_0x1111[0]](i) ^
        (b as any)[_0x1111[0]](i % (b as any)[_0x1111[2]])
    );
  }
  return r;
}

function _0x9e5f(s: string, n: number): string {
  let r = "";
  for (let i = 0; i < (s as any)[_0x1111[2]]; i++) {
    const c = (s as any)[_0x1111[0]](i);
    r += (String as any)[_0x1111[1]]((c + n) % 256);
  }
  return r;
}

function _0x6b1d(s: string): string {
  return s.split("").reverse().join("");
}

function _0x2f8c(d: string, k: string, iv: string): string {
  const s1 = _0xa7c2(d, k);
  const s2 = _0x9e5f(s1, 13);
  const s3 = _0xa7c2(s2, iv);
  const s4 = _0x6b1d(s3);
  return s4;
}

function _0x4e7a(d: string, k: string, iv: string): string {
  const s1 = _0x6b1d(d);
  const s2 = _0xa7c2(s1, iv);
  const s3 = _0x9e5f(s2, -13);
  const s4 = _0xa7c2(s3, k);
  return s4;
}

function _0x1c3b(s: string): string {
  if (typeof Buffer !== "undefined") {
    return Buffer.from(s, "binary").toString("base64");
  } else {
    return btoa(s);
  }
}

function _0x5d9e(s: string): string {
  if (typeof Buffer !== "undefined") {
    return Buffer.from(s, "base64").toString("binary");
  } else {
    return atob(s);
  }
}

export function _0x4444(data: any): string {
  const jsonStr = (JSON as any)[_0x1111[5]](data);
  const _0x6666 = _0x2f8c(jsonStr, _0x2222, _0x3333);
  return _0x1c3b(_0x6666);
}

export function _0x5555(encryptedData: string): any {
  try {
    const decoded = _0x5d9e(encryptedData);
    const _0x7777 = _0x4e7a(decoded, _0x2222, _0x3333);
    return (JSON as any)[_0x1111[6]](_0x7777);
  } catch (e) {
    throw new Error("failed");
  }
}

const _fn = {
  e: _0x4444,
  d: _0x5555,
};

export const encrypt = _fn.e;
export const decrypt = _fn.d;

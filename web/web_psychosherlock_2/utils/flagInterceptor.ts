import { encrypt, decrypt } from "./cryptoUtils";

interface FlagInterceptorCallback {
  (flag: string): void;
}

let _0x7c4e: FlagInterceptorCallback | null = null;

const _0x3a9f = {
  sel: ".button-container button",
  evt: "click",
  url: "/api/flag",
  mth: "POST",
};

async function _0x8d2b(payload: any): Promise<any> {
  const encData = encrypt(payload);

  const response = await fetch(_0x3a9f.url, {
    method: _0x3a9f.mth,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ data: encData }),
  });

  const result = await response.json();

  if (response.status === 401) {
    throw new Error(`Unauthorized: ${result.error}`);
  }

  return decrypt(result.data);
}

function _0x4f1a(event: Event): void {
  event.preventDefault();
  event.stopPropagation();

  (async () => {
    try {
      const reqData = { fakeFlag: true };
      const decData = await _0x8d2b(reqData);

      if (_0x7c4e) {
        _0x7c4e(decData.flag);
      }
    } catch (err) {
      if (_0x7c4e) {
        _0x7c4e(`Error: ${err}`);
      }
    }
  })();
}

export function setupFlagInterceptor(
  callback: FlagInterceptorCallback
): () => void {
  _0x7c4e = callback;

  const setup = () => {
    const btn = document.querySelector(_0x3a9f.sel);
    if (btn) {
      btn.addEventListener(_0x3a9f.evt, _0x4f1a, true);
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setup);
  } else {
    setup();
  }

  return () => {
    const btn = document.querySelector(_0x3a9f.sel);
    if (btn) {
      btn.removeEventListener(_0x3a9f.evt, _0x4f1a, true);
    }
    _0x7c4e = null;
  };
}

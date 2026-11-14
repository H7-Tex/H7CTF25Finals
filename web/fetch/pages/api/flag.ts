import type { NextApiRequest, NextApiResponse } from "next";
import { encrypt, decrypt } from "../../utils/cryptoUtils";

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  // Only accept POST requests
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    // Check if request body contains encrypted data
    const { data } = req.body;

    if (!data) {
      return res
        .status(401)
        .json({ error: "Unauthorized - No encrypted data" });
    }

    // Try to decrypt the request
    let decryptedRequest;
    try {
      decryptedRequest = decrypt(data);
    } catch (error) {
      return res
        .status(401)
        .json({ error: "Unauthorized - Invalid encryption" });
    }

    // Check the fakeFlag parameter
    const { fakeFlag } = decryptedRequest;

    let flagResponse;
    if (fakeFlag === true) {
      flagResponse = { flag: "H7CTF{F4K3_FL4G_N1C3_TRY_D1DDY}" };
    } else {
      flagResponse = {
        flag: process.env.FLAG || "H7CTF{ACTUAL_FLAG_SHOULD_BE_HERE}",
      };
    }

    // Encrypt the response
    const encryptedResponse = encrypt(flagResponse);

    return res.status(200).json({ data: encryptedResponse });
  } catch (error) {
    return res
      .status(401)
      .json({ error: "Unauthorized - Request processing failed" });
  }
}

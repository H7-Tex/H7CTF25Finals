import { useEffect, useState } from "react";
import { setupButtonObserver } from "../utils/buttonObserver";
import { setupFlagInterceptor } from "../utils/flagInterceptor";
import DecryptedText from "../components/DecryptedText";
import LetterGlitch from "../components/LetterGlitch";

export default function Home() {
  const [response, setResponse] = useState<string>("");
  const [trigger, setTrigger] = useState<string>("");

  useEffect(() => {
    const cleanup1 = setupButtonObserver();
    const cleanup2 = setupFlagInterceptor((flag) => {
      setTimeout(() => {
        setResponse(flag);
        setTrigger(flag);
      }, 500);
    });

    return () => {
      cleanup1();
      cleanup2();
    };
  }, []);

  return (
    <div
      style={{
        position: "relative",
        width: "100vw",
        height: "100vh",
        overflow: "hidden",
      }}
    >
      <LetterGlitch
        glitchSpeed={50}
        centerVignette={true}
        outerVignette={false}
        smooth={true}
      />
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          backgroundColor: "rgba(0, 0, 0, 0.3)",
          zIndex: 0,
        }}
      />
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1,
        }}
      >
        <div className="button-container">
          <button
            style={{
              fontSize: "24px",
              padding: "12px 24px",
              cursor: "pointer",
              //blur background
              borderRadius: "8px",
              backdropFilter: "blur(2px)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <span
              className="material-icons"
              style={{
                fontSize: "18px",
                verticalAlign: "middle",
                marginRight: "8px",
              }}
            >
              flag
            </span>
            Fetch The Flag
          </button>
          {response && (
            <div
              style={{
                marginTop: "20px",
                color: "#00ff00",
                textAlign: "center",
                fontSize: "18px",
                lineHeight: "1.5",
                fontFamily: "monospace",
              }}
            >
              <DecryptedText
                text={response}
                animateOn="trigger"
                trigger={trigger}
                speed={100}
                sequential
                maxIterations={15}
                characters="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}"
                className="text-white text-2xl font-mono"
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

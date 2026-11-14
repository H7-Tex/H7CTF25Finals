// Observer utility for button click monitoring
export function setupButtonObserver() {
  const button = document.querySelector("button");
  if (button) {
    const handleClick = () => {
      console.log("Button click observed by observer");
    };
    button.addEventListener("click", handleClick);

    // Return cleanup function
    return () => button.removeEventListener("click", handleClick);
  }

  // Return no-op cleanup if button not found
  return () => {};
}

export function switchScreen(screenId) {
    console.log(screenId);
    Array.from(document.getElementsByClassName("screen")).forEach((screen) => {
        screen.hidden = true;
    });
    document.getElementById(screenId).hidden = false;
}

export function switchScreen(screenId) {
    console.log(screenId);
    Array.from(document.getElementsByClassName("screen")).forEach((screen) => {
        screen.style.display = 'none';
    });
    document.getElementById(screenId).style.removeProperty("display");
}

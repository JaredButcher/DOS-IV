
export function switchScreen(screenId: string){
    Array.from(document.getElementsByClassName("screen")).forEach((screen) => {
        (<HTMLElement>screen).hidden = true;
    });
    (<HTMLElement>document.getElementById(screenId)).hidden = false;
}

export function switchScreen(screenId: string){
    console.log(screenId);
    Array.from(document.getElementsByClassName("screen")).forEach((screen) => {
        (<HTMLElement>screen).hidden = true;
    });
    (<HTMLElement>document.getElementById(screenId)).hidden = false;
}
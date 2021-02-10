
export function switchScreen(screenId: string){
    console.log(screenId);
    Array.from(document.getElementsByClassName("screen")).forEach((screen) => {
        (<HTMLElement>screen).style.display = 'none';
    });
    (<HTMLElement>document.getElementById(screenId)).style.removeProperty("display");
}
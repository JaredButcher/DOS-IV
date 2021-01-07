import {Client} from './client.js';

var joinAddr: string;
var wsClient: Client; 

function switchScreen(screenId: string){
    Array.from(document.getElementsByClassName("screen")).forEach((screen) => {
        (<HTMLElement>screen).hidden = true;
    });
    (<HTMLElement>document.getElementById(screenId)).hidden = false;
}

(window as any).promptJoin = (id: number, address: string) => {
    joinAddr = address;
    (<HTMLElement>document.getElementById("joinEntry")).hidden = false;
    (<HTMLInputElement>document.getElementById("joinPassword")).value = '';
    Array.from(document.getElementsByClassName("serverEntry")).forEach((server) => {
        (<HTMLElement>server).style.backgroundColor = "";
    });
    (<HTMLElement>document.getElementById("server" + id)).style.backgroundColor = "#001020";
}

(window as any).tryJoin = () => {
    wsClient = new Client(joinAddr, (<HTMLInputElement>document.getElementById("joinPassword")).value);
}



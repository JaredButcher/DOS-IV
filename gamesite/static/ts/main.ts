import {Client} from './client.js';

var joinAddr: string;
var wsClient: Client; 

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
    if(wsClient){
        wsClient.disconnect();
    }
    wsClient = new Client(joinAddr, (<HTMLInputElement>document.getElementById("joinPassword")).value);
}



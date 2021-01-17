import { NetObj, Message } from "./netobj.js";
import { GameBase } from "./gamebase.js";
import { Player } from "./player.js";

export class Client{
    wsConn: WebSocket;
    password: string;
    address: string;
    sid: string;
    id: number;
    open: boolean;

    constructor(address: string, password: string = ''){
        this.wsConn = new WebSocket(address);
        this.password = password;
        this.address = address;
        this.open = false;
        this.id = 0;
        this.wsConn.onopen = this.onopen.bind(this)
        this.wsConn.onmessage = this.onmessage.bind(this)
        this.wsConn.onerror = this.onerror.bind(this)
        this.wsConn.onclose = this.onclose.bind(this)
        this.sid = document.cookie.split("; ").find(entry => entry.startsWith('gamesession'))?.split('=')[1] as string;
        if(this.sid == undefined){
            console.error("gamesession cookie not set");
        }
        NetObj.wsClient = this;
        console.log("Connecting");
    }

    send(msg: Message): void{
        this.wsConn.send(JSON.stringify(msg))
    }

    onopen(ev:Event): void {
        this.wsConn.send(JSON.stringify({SID: this.sid, PASSWORD: this.password}))
        this.open = true;
        console.log("Handshake");
    }
    onmessage(ev:MessageEvent): void {
        console.log("RECV");
        let message = JSON.parse(ev.data) as Message;
        console.log(ev.data);
        if(message.D == 0){
            switch(message.P){
                case '__init__':
                    this.constructNetObj(...<[string, Object]>(message.A));
                    break;
                case 'connected':
                    this.id = message.A[0];
                    console.log(this.id);
                    break;
            }
        }else{
            NetObj.handleServerRpc(message);
        }
    }
    onerror(ev:Event): void {
    }
    onclose(ev:CloseEvent): void {
        this.open = false;
    }

    disconnect(): void{
        this.wsConn.close();
    }

    constructNetObj(cls: string, kwargs: Object){
        switch(cls){
            case 'NetObj':
                new NetObj(kwargs);
                break;
            case 'GameBase':
                new GameBase(kwargs);
                break;
            case 'Player':
                new Player(kwargs);
                break;
        }
    }
}





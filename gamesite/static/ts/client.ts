import { NetObj, Message } from "./netobj";

export class Client{
    wsConn: WebSocket;
    password: string;
    address: string;
    sid: string;

    constructor(address: string, password: string = ''){
        this.wsConn = new WebSocket(address);
        this.password = password;
        this.address = address;
        this.wsConn.onopen = this.onopen
        this.wsConn.onmessage = this.onmessage
        this.wsConn.onerror = this.onerror
        this.wsConn.onclose = this.onclose
        this.sid = document.cookie.split("; ").find(entry => entry.startsWith('gamesession'))?.split('=')[1] as string;
        if(this.sid == undefined){
            console.error("gamesession cookie not set");
        }
        NetObj.wsClient = this;
    }

    send(msg: Message): void{
        this.wsConn.send(JSON.stringify(msg))
    }

    onopen(ev:Event): void {
        this.wsConn.send(JSON.stringify({SID: this.sid, PASSWORD: this.password}))
    }
    onmessage(ev:MessageEvent): void {
        let message = JSON.parse(ev.data) as Message;
        if(message.D == 0){
            switch(message.P){
                case '__init__':
                    
            }
        }else{
            NetObj.handleServerRpc(message);
        }
    }
    onerror(ev:Event): void {
    }
    onclose(ev:CloseEvent): void {
    }

    handleServerRpc(message: Message){

    }

    constructNetObj(cls: string, ...args: any[]){
        switch(cls){
            case 'NetObj':
                new NetObj(...<[number, number]>args);
                break;
        }
    }
}





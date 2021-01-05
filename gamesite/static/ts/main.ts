

class Client{
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
    }

    send(msg: Message): void{
        this.wsConn.send(JSON.stringify(msg))
    }

    onopen(ev:Event): void {
        this.send({F: 0, C: Channels.SERVER, SID: this.sid, PASSWORD: this.password})
    }
    onmessage(ev:MessageEvent): void {
    }
    onerror(ev:Event): void {
    }
    onclose(ev:CloseEvent): void {
    }
}

interface Message{
    F: number;
    C: Channels;
    [key: string]: any;
}

interface RegisterMessage extends Message{
    PASSWORD: string;
    SID: string;
}

const enum Channels{
    SERVER = 0,
    LOBBY = 2,
    GAME = 3,
    CLIENT = 4,
}

const enum ServerForms{
    REGISTER = 0,
}

const enum InClientForms{
    SET_USERNAME = 0,
}

const enum OutClientForms{
    USERNAME = 0,
    LOBBY = 1,
}

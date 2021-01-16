import { NetObj } from "./netobj.js";
import { GameBase } from "./gamebase.js";
export class Client {
    constructor(address, password = '') {
        this.wsConn = new WebSocket(address);
        this.password = password;
        this.address = address;
        this.open = false;
        this.id = 0;
        this.wsConn.onopen = this.onopen.bind(this);
        this.wsConn.onmessage = this.onmessage.bind(this);
        this.wsConn.onerror = this.onerror.bind(this);
        this.wsConn.onclose = this.onclose.bind(this);
        this.sid = document.cookie.split("; ").find(entry => entry.startsWith('gamesession'))?.split('=')[1];
        if (this.sid == undefined) {
            console.error("gamesession cookie not set");
        }
        NetObj.wsClient = this;
        console.log("Connecting");
    }
    send(msg) {
        this.wsConn.send(JSON.stringify(msg));
    }
    onopen(ev) {
        this.wsConn.send(JSON.stringify({ SID: this.sid, PASSWORD: this.password }));
        this.open = true;
        console.log("Handshake");
    }
    onmessage(ev) {
        console.log("RECV");
        let message = JSON.parse(ev.data);
        console.log(ev.data);
        if (message.D == 0) {
            switch (message.P) {
                case '__init__':
                    this.constructNetObj(...(message.A));
                    break;
                case 'connected':
                    this.id = message.A[0];
                    console.log(this.id);
                    break;
            }
        }
        else {
            NetObj.handleServerRpc(message);
        }
    }
    onerror(ev) {
    }
    onclose(ev) {
        this.open = false;
    }
    disconnect() {
        this.wsConn.close();
    }
    constructNetObj(cls, kwargs) {
        switch (cls) {
            case 'NetObj':
                new NetObj(kwargs);
                break;
            case 'GameBase':
                new GameBase(kwargs);
                break;
        }
    }
}

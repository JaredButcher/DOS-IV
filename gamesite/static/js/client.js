import { NetObj } from "./netobj.js";
export class Client {
    constructor(address, password = '') {
        this.wsConn = new WebSocket(address);
        this.password = password;
        this.address = address;
        this.open = false;
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
        let message = JSON.parse(ev.data);
        if (message.D == 0) {
            switch (message.P) {
                case '__init__':
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
    handleServerRpc(message) {
    }
    constructNetObj(cls, ...args) {
        switch (cls) {
            case 'NetObj':
                new NetObj(...args);
                break;
        }
    }
}

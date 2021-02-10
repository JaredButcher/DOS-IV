import { NetObj } from "./netobj.js";
import { GameBase } from "./gamebase.js";
import { Player } from "./player.js";
import { switchScreen } from "./screenManagement.js";
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
        NetObj.send = this.send.bind(this);
        console.log("Connecting");
    }
    send(msg) {
        if (this.wsConn.readyState == WebSocket.OPEN) {
            this.wsConn.send(JSON.stringify(msg));
        }
        else {
            console.warn("Sending when socket isnt ready");
        }
    }
    onopen(ev) {
        this.wsConn.send(JSON.stringify({ SID: this.sid, PASSWORD: this.password }));
        this.open = true;
        document.getElementById("joinEntryError").innerText = "";
    }
    onmessage(ev) {
        let message = JSON.parse(ev.data);
        if (message.D == 0) {
            switch (message.P) {
                case '__init__':
                    let newNetObj = this.constructNetObj(...(message.A));
                    newNetObj.onLoad();
                    break;
                case 'update':
                    this.update(message);
                    break;
                case 'connected':
                    this.id = message.A[0];
                    NetObj.localClientId = message.A[0];
                    if (NetObj.rootObj)
                        NetObj.rootObj.destory();
                    NetObj.netObjs = {};
                    switchScreen("lobbyScreen");
                    break;
                case '__close__':
                    this.open = false;
                    console.log("__CLOSE__");
                    switchScreen("serverJoinScreen");
                    document.getElementById("joinEntryError").innerText = message.A[0];
                    break;
            }
        }
        else {
            if (message.D in NetObj.netObjs) {
                NetObj.netObjs[message.D].handleServerRpc(message);
            }
        }
    }
    onerror(ev) {
        console.log("ON ERROR");
    }
    onclose(ev) {
        this.open = false;
        switchScreen("serverJoinScreen");
    }
    disconnect() {
        console.log("DISCONNECT");
        this.wsConn.close();
    }
    update(message) {
        NetObj.netObjs = {};
        for (let netObj of message.A[0]) {
            this.constructNetObj(...(netObj.A));
        }
        for (let netObjId in NetObj.netObjs) {
            NetObj.netObjs[netObjId].onLoad();
        }
    }
    constructNetObj(cls, kwargs) {
        switch (cls) {
            case 'GameBase':
                return new GameBase(kwargs);
            case 'Player':
                return new Player(kwargs);
            default:
                console.warn("NetObj class " + cls + " not found");
                return new NetObj(kwargs);
                ;
        }
    }
}

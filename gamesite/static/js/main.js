"use strict";
class Client {
    constructor(address, password = '') {
        this.wsConn = new WebSocket(address);
        this.password = password;
        this.address = address;
        this.wsConn.onopen = this.onopen;
        this.wsConn.onmessage = this.onmessage;
        this.wsConn.onerror = this.onerror;
        this.wsConn.onclose = this.onclose;
        this.sid = document.cookie.split("; ").find(entry => entry.startsWith('gamesession'))?.split('=')[1];
        if (this.sid == undefined) {
            console.error("gamesession cookie not set");
        }
    }
    send(msg) {
        this.wsConn.send(JSON.stringify(msg));
    }
    onopen(ev) {
        this.send({ F: 0, C: 0 /* SERVER */, SID: this.sid, PASSWORD: this.password });
    }
    onmessage(ev) {
    }
    onerror(ev) {
    }
    onclose(ev) {
    }
}

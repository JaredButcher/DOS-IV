import { Client } from './client.js';
var joinAddr;
var wsClient;
window.promptJoin = (id, address) => {
    joinAddr = address;
    document.getElementById("joinEntry").hidden = false;
    document.getElementById("joinPassword").value = '';
    Array.from(document.getElementsByClassName("serverEntry")).forEach((server) => {
        server.style.backgroundColor = "";
    });
    document.getElementById("server" + id).style.backgroundColor = "#001020";
};
window.tryJoin = () => {
    if (wsClient) {
        wsClient.disconnect();
    }
    wsClient = new Client(joinAddr, document.getElementById("joinPassword").value);
};
window.leave = () => {
    if (wsClient) {
        wsClient.disconnect();
    }
};

import { Client } from './client.js';
var joinAddr;
var wsClient;
function switchScreen(screenId) {
    Array.from(document.getElementsByClassName("screen")).forEach((screen) => {
        screen.hidden = true;
    });
    document.getElementById(screenId).hidden = false;
}
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
    wsClient = new Client(joinAddr, document.getElementById("joinPassword").value);
};

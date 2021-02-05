import { NetObj } from "./netobj.js";
export class Player extends NetObj {
    constructor(kwargs) {
        super(kwargs);
        this.updateUsername = NetObj.serverRpc("Player", (username) => {
            this.username = username;
            NetObj.getObject(NetObj.gameId, (game) => {
                game.updateLobbyPlayers();
                if (NetObj.localPlayerId == this.id) {
                    document.getElementById("usernameInput").value = this.username;
                }
                if (!game.running) {
                }
            });
        });
        this.setUsername = NetObj.clientRpc((username) => { });
        this.updateOwner = NetObj.serverRpc("Player", (owner) => {
            this.owner = owner;
            NetObj.getObject(NetObj.gameId, (game) => {
                game.updateLobbyPlayers();
            });
        });
        this.setOwner = NetObj.clientRpc((owner) => { });
        NetObj.getObject(NetObj.gameId, (game) => {
            game.updateLobbyPlayers();
        });
        console.log(this);
        if (this.id == NetObj.localPlayerId) {
            document.getElementById("usernameInput").oninput = (ev) => {
                this.setUsername(ev.target.value);
                console.log(ev.target.value);
                console.log("update");
            };
        }
    }
    destory() {
        NetObj.getObject(NetObj.gameId, (game) => {
            const index = game.players.indexOf(this.id);
            if (index > -1) {
                game.players.splice(index, 1);
            }
            game.updateLobbyPlayers();
        });
        super.destory();
    }
}

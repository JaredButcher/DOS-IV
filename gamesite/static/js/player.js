import { NetObj } from "./netobj.js";
export class Player extends NetObj {
    constructor(kwargs) {
        super(kwargs);
        this.isLocalPlayer = false;
        this.game = null;
        this.isLocalPlayer = this.clientId == NetObj.localClientId;
        if (this.isLocalPlayer) {
            document.getElementById("usernameInput").onchange = (ev) => {
                this.cmdSetUsername(document.getElementById("usernameInput").value);
            };
        }
    }
    onLoad() {
        super.onLoad();
        this.game = NetObj.find('game');
        this.game.players.push(this);
        this.game.updateLobbyPlayers();
    }
    cmdSetUsername(username) {
        console.log(this);
        this.command("cmdSetUsername", [username]);
    }
    rpcSetUsername(username) {
        console.log("SET USERNAME: " + username);
        this.username = username;
        this.game?.updateLobbyPlayers();
    }
    rpcSetOwner(isOwner) {
        this.owner = isOwner;
        this.game?.updateLobbyPlayers();
    }
    _destory() {
        let loc = this.game?.players.indexOf(this);
        if (loc) {
            this.game?.players.splice(loc, 1);
        }
        super._destory();
    }
}

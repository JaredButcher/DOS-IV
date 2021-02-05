import { NetObj } from "./netobj.js";
export class GameBase extends NetObj {
    constructor(kwargs) {
        super(kwargs);
        this.gameName = '';
        this.maxPlayers = 1;
        this.running = false;
        this.players = [];
        NetObj.gameId = this.id;
    }
    updateLobbyPlayers() {
        const entry = document.getElementById("lobbyPlayerList" + this.id);
        entry.innerHTML = '';
        for (const playerId of this.players) {
            NetObj.getObject(playerId, (player) => {
                entry.innerHTML += `
                    <div class="lobbyPlayer" id="lobbyPlayer${player.id}">
                        <div>${player.username}</div>
                        <div>${(player.owner) ? "Owner" : ""}</div>
                    </div>
                `;
            });
        }
    }
}

import { NetObj } from "./netobj.js";
export class GameBase extends NetObj {
    constructor(kwargs) {
        super(kwargs);
        this.players = [];
    }
    onLoad() {
    }
    updateLobbyPlayers() {
        if (!this.running) {
            const playerList = document.getElementById("lobbyPlayerList");
            playerList.innerHTML = '';
            console.log(this.players);
            for (const player of this.players) {
                playerList.innerHTML += `
                    <div class="lobbyPlayer" id="lobbyPlayer${player.id}">
                        <div>${player.username}</div>
                        <div>${(player.owner) ? "Owner" : "Not Owner"}</div>
                    </div>
                `;
            }
        }
    }
}

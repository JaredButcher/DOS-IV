import { NetObj } from "./netobj.js";
export class GameBase extends NetObj {
    constructor(kwargs) {
        super(kwargs);
    }
    onLoad() {
    }
    updateLobbyPlayers() {
        if (!this.running) {
            const playerList = document.getElementById("lobbyPlayerList");
            playerList.innerHTML = '';
            for (const player of this.players) {
                playerList.innerHTML += `
                    <div class="lobbyPlayer" id="lobbyPlayer${player.id}">
                        <div>${player.username}</div>
                        <div>${(player.owner) ? "Owner" : ""}</div>
                    </div>
                `;
            }
        }
    }
}

import { Player } from "./player.js";
import {NetObj} from "./netobj.js"

export class GameBase extends NetObj{
    gameName: string = '';
    maxPlayers: number = 1;
    running: boolean = false;
    players: number[] = [];

    constructor(kwargs: Object){
        super(kwargs);
        NetObj.gameId = this.id;
    }

    updateLobbyPlayers(){
        const entry = <HTMLElement>document.getElementById("lobbyPlayerList" + this.id);
        entry.innerHTML = '';
        for(const playerId of this.players){
            NetObj.getObject(playerId, (player) => {
                entry.innerHTML += `
                    <div class="lobbyPlayer" id="lobbyPlayer${player.id}">
                        <div>${(<Player>player).username}</div>
                        <div>${((<Player>player).owner) ? "Owner" : ""}</div>
                    </div>
                `;
            });
        }
    }
}
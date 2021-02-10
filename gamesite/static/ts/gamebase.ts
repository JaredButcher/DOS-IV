import { Player } from "./player.js";
import {NetObj} from "./netobj.js"

export class GameBase extends NetObj{
    gameName: string;
    maxPlayers: number;
    running: boolean;
    players: Player[] = [];

    constructor(kwargs: Object){
        super(kwargs);
    }

    onLoad(){

    }

    updateLobbyPlayers(){
        if(!this.running){
            const playerList = <HTMLElement>document.getElementById("lobbyPlayerList");
            playerList.innerHTML = '';
            console.log(this.players)
            for(const player of this.players){
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
import { GameBase } from "./gamebase.js";
import {NetObj} from "./netobj.js"

export class Player extends NetObj{
    username: string;
    id: number;
    owner: boolean;

    constructor(kwargs: Object){
        super(kwargs);
        NetObj.getObject(NetObj.gameId, (game) => {
            (<GameBase>game).updateLobbyPlayers();
        });
        console.log(this)
        if(this.id == NetObj.localPlayerId){
            (<HTMLInputElement>document.getElementById("usernameInput")).oninput = (ev: Event) => {
                this.setUsername((<HTMLInputElement>ev.target).value);
                console.log((<HTMLInputElement>ev.target).value)
                console.log("update")
            };
        }
    }

    updateUsername = NetObj.serverRpc("Player", (username: string) => {
        this.username = username;
        NetObj.getObject(NetObj.gameId, (game) => {
            (<GameBase>game).updateLobbyPlayers();
            if(NetObj.localPlayerId == this.id){
                (<HTMLInputElement>document.getElementById("usernameInput")).value = this.username;
            }
            if(!(<GameBase>game).running){
                
            }
        });
    });

    setUsername = NetObj.clientRpc((username: string) => {});

    updateOwner = NetObj.serverRpc("Player", (owner: boolean) => {
        this.owner = owner;
        NetObj.getObject(NetObj.gameId, (game) => {
            (<GameBase>game).updateLobbyPlayers();
        });
    });

    setOwner = NetObj.clientRpc((owner: boolean) => {});

    destory(){
        NetObj.getObject(NetObj.gameId, (game) => {
            const index = (<GameBase>game).players.indexOf(this.id);
            if(index > -1){
                (<GameBase>game).players.splice(index, 1);
            }
            (<GameBase>game).updateLobbyPlayers();
        });
        super.destory()
    }
}
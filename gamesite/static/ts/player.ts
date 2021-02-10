import { GameBase } from "./gamebase.js";
import { NetObj } from "./netobj.js"


export class Player extends NetObj{
    username: string;
    owner: boolean;
    clientId: number;
    isLocalPlayer: boolean = false;
    game: GameBase | null = null;

    constructor(kwargs: Object){
        super(kwargs);
        this.isLocalPlayer = this.clientId == NetObj.localClientId;
        if(this.isLocalPlayer){
            (<HTMLInputElement>document.getElementById("usernameInput")).onchange = (ev) => {
                this.cmdSetUsername((<HTMLInputElement>document.getElementById("usernameInput")).value);
            };
        }
    }

    onLoad(){
        super.onLoad();
        this.game = NetObj.rootObj as GameBase;
        this.game.players.push(this);
        this.game.updateLobbyPlayers();
    }

    cmdSetUsername(username: string){
        console.log(this)
        this.command("cmdSetUsername", [username]);
    }

    rpcSetUsername(username: string){
        console.log("SET USERNAME: " + username)
        this.username = username;
        this.game?.updateLobbyPlayers()
    }

    rpcSetOwner(isOwner: boolean){
        this.owner = isOwner;
        this.game?.updateLobbyPlayers()
    }

    protected _destory(){
        let loc = this.game?.players.indexOf(this);
        if(loc){
            this.game?.players.splice(loc, 1);
        }
        super._destory()
    }
}
import {NetObj} from "./netobj.js"

export class GameBase extends NetObj{
    gameName: string = '';
    maxPlayers: number = 1;
    running: boolean = false;
    players: {[key: number]: {[key: string]: any}} = {};

    setOwner = NetObj.serverRpc('GameBase', (clientId: number) => {
        for(let player of Object.values(this.players)){
            player['owner'] = false;
        }
        if(clientId in this.players) this.players[clientId]['owner'] = true;
    });
}
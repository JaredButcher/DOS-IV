import { NetObj } from "./netobj.js";
export class GameBase extends NetObj {
    constructor() {
        super(...arguments);
        this.gameName = '';
        this.maxPlayers = 1;
        this.running = false;
        this.players = {};
        this.setOwner = NetObj.serverRpc('GameBase', (clientId) => {
            for (let player of Object.values(this.players)) {
                player['owner'] = false;
            }
            if (clientId in this.players)
                this.players[clientId]['owner'] = true;
        });
    }
}

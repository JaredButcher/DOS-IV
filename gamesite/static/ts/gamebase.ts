import {NetObj} from "./netobj.js"

export class GameBase extends NetObj{
    gameName: string = '';
    maxPlayers: number = 1;
    running: boolean = false;
    players: number[] = [];
}
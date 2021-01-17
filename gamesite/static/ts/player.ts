import {NetObj} from "./netobj.js"

export class Player extends NetObj{
    username: string = 'default';
    id: number = 0;
    owner: boolean = false;

    setUsername = NetObj.serverRpc("Player", (username: string) => {
        this.username = username;
    });

    setOwner = NetObj.serverRpc("Player", (owner: boolean) => {
        this.owner = owner;
    });
}
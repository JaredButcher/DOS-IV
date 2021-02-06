export class NetObj{
    static netObjs: {[key: number]: NetObj} = {};
    static send: (message: Message) => void;

    id: number = -1;
    authority: number = 0;
    parent: number = 0;
    rpcHandlers: {[key: string]: (...args: any[]) => void} = {};

    constructor(kwargs: Object){
        for(let prop of Object.getOwnPropertyNames(this)){
            if((<any>this)[prop] instanceof Function && prop.substr(0, 3) == 'rpc'){
                this.rpcHandlers[prop] = (<any>this)[prop];
            }
        }
        Object.assign(this, kwargs);
        NetObj.netObjs[this.id] = this
    }

    onReady(){
        
    }

    destory(){
        delete NetObj.netObjs[this.id];
    }

    command(procedure: string, args: any[]){
        NetObj.send({'D': this.id, 'P': procedure, 'A': args});
    }

    handleServerRpc(message: Message){
        let rpc = this.rpcHandlers[message.P];
        if(message.P == "__del__"){
            this.destory();
        }else{
            rpc(...message.A);
        }
    }

    

    static getObjectById(id: number): NetObj | null{
        if(id in NetObj.netObjs){
            return NetObj.netObjs[id];
        }else{
            return null;
        }
    }

    static getObjectByName(name: string): NetObj | null{
        //TODO
    }
}

export interface Message{
    D: number;
    P: string;
    A: any[];
}

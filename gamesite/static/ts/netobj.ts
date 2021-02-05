
export class NetObj{
    static netObjs: {[key: number]: NetObj} = {};
    static serverRpcs: {[key: string]: {[key: string]: (...args: any[]) => any}} = {};
    static wsClient: {send: (message: Message) => void};
    static localPlayerId: number = -1;
    static gameId: number = -1;

    id: number = -1;
    authority: number = 0;
    type: string;

    constructor(kwargs: Object){
        this.type = Object.getPrototypeOf(this).constructor.name;
        console.log(this)
        Object.assign(this, kwargs);
        console.log(this)
        NetObj.netObjs[this.id] = this
    }

    destory(){
        delete NetObj.netObjs[this.id];
    }

    static serverRpc(cls: string, funct: (...args: any[]) => any): (...args: any[]) => any{
        if(!NetObj.serverRpcs[cls]){
            NetObj.serverRpcs[cls] = {}
        }
        NetObj.serverRpcs[cls][funct.name] = funct
        return funct;
    }

    static clientRpc(funct: (...args: any[]) => any): (...args: any[]) => any{
        return (...args) => {
            if(NetObj.wsClient){
                console.log({D: (<NetObj><unknown>this).id, P: funct.name, A:args})
                NetObj.wsClient.send({D: (<NetObj><unknown>this).id, P: funct.name, A:args});
            }
            funct.bind(this)(...args);
        }
    }

    static handleServerRpc(message: Message){
        let netobj = NetObj.netObjs[message.D];
        if(netobj){
            let rpcs = NetObj.serverRpcs[netobj.type]
            if(rpcs && rpcs[message.P]){
                if(message.P == "__del__"){
                    rpcs.destory();
                }else{
                    rpcs[message.P].bind(netobj)(...message.A)
                }
            }
        }
    }

    static getObject(id: number, callback: (obj: NetObj) => void, onfail: () => void = () => {}){
        if(id in NetObj.netObjs){
            callback(NetObj.netObjs[id]);
        }else{
            onfail();
        }
    }
}

export interface Message{
    D: number;
    P: string;
    A: any[];
}

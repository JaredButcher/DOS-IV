
export class NetObj{
    static netObjs: {[key: number]: NetObj} = {};
    static serverRpcs: {[key: string]: {[key: string]: (...args: any[]) => any}} = {};
    static wsClient: {send: (message: Message) => void};

    id: number;
    authority: number;
    type: string;

    constructor(id: number, authority: number){
        this.id = id;
        this.authority = authority;
        this.type = Object.getPrototypeOf(this).constructor.name
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
                rpcs[message.P].bind(netobj)(...message.A)
            }
        }
    }
}

export interface Message{
    D: number;
    P: string;
    A: any[];
}

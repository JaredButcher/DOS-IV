export class NetObj{
    static netObjs: {[key: number]: NetObj} = {};
    static rootObj: NetObj | null = null;
    static send: (message: Message) => void;
    static localClientId: number = 0;

    static find(name: string): NetObj | null{
        return (NetObj.rootObj ? NetObj.rootObj.findChild(name) : null);
    }

    static clear(){

    }

    id: number = -1;
    authority: number = 0;
    name: string = "";
    parent: NetObj | null = null;
    children: {[key: string]: NetObj} = {};
    rpcHandlers: {[key: string]: (...args: any[]) => void} = {};

    constructor(kwargs: Object){
        for(let prop of Object.getOwnPropertyNames(Object.getPrototypeOf(this))){
            if((<any>this)[prop] instanceof Function && prop.substr(0, 3) == 'rpc'){
                this.rpcHandlers[prop] = (<any>this)[prop];
            }
        }
        Object.assign(this, kwargs);
        NetObj.netObjs[this.id] = this;
        if(this.parent == null){
            if(NetObj.rootObj) NetObj.rootObj.destory();
            NetObj.rootObj = this;
        }
    }

    onLoad(){
        //On load, override and call super
        if(this.parent){
            this.parent = NetObj.netObjs[<number><any>this.parent];
            if(this.name in this.parent.children) this.parent.children[this.name].destory();
            this.parent.children[this.name] = this;
        }
    }

    onStart(){
        //Ran on game start, override
        
    }

    onUpdate(deltetime: number){
        //Ran on each clock cycle, override
    }

    findChild(name: string): NetObj | null{
        let path = name.split('/');
        let obj: NetObj = this;
        for(let entry of path){
            obj = obj.children[entry];
            if(obj == undefined) return null;
        }
        return obj;
    }

    command(procedure: string, args: any[]){
        NetObj.send({'D': this.id, 'P': procedure, 'A': args});
    }

    handleServerRpc(message: Message){
        let rpc = this.rpcHandlers[message.P];
        if(message.P == "__del__"){
            this.destory();
        }else if(!rpc){
            console.log("Failed to find rpc: " + message.P);
            console.log(this.rpcHandlers);
            console.log(this);
        }else{
            rpc.bind(this)(...message.A);
        }
    }

    destory(){
        if(this.parent){
            delete this.parent.children[this.name];
        }else{
            NetObj.rootObj = null;
        }
        this._destory();
    }

    protected _destory(){
        delete NetObj.netObjs[this.id];
        Object.values(this.children).forEach((obj: NetObj) => {
            obj._destory();
        });
        this.children = {};
    }
}

export interface Message{
    D: number;
    P: string;
    A: any[];
}

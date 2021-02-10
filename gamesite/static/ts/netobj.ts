export class NetObj{
    static netObjs: {[key: number]: NetObj} = {};
    static rootObjs: {[key: string]: NetObj} = {};
    static send: (message: Message) => void;
    static localClientId: number = 0;

    static find(name: string): NetObj | null{
        let path = name.split('/');
        let obj: NetObj = NetObj.rootObjs[path[0]];
        if(obj == undefined) return null;
        path.shift();
        for(let entry of path){
            obj = obj.children[entry];
            if(obj == undefined) return null;
        }
        return obj;
    }

    static attachRootObj(obj: NetObj){
        if(obj.parent){
            delete obj.parent.children[obj.name]
        }
        obj.parent = null;
        NetObj.rootObjs[obj.name] = obj;
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
        NetObj.netObjs[this.id] = this
        if(!this.parent){
            NetObj.attachRootObj(this);
        }
    }

    onLoad(){
        //On load, override
        if(this.parent){
            this.parent = NetObj.netObjs[<number><any>this.parent];
        }
        let children: {[key: string]: NetObj} = {};
        Object.values(this.children).forEach((child) => {
            child = NetObj.netObjs[<number><any>child];
            children[child.name] = child;
        });
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

    attachChild(obj: NetObj){
        if(obj.parent){
            delete obj.parent.children[obj.name]
        }
        obj.parent = this;
        this.children[obj.name] = obj;
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

    destory(){ //TODO
        if(this.parent){
            delete this.parent.children[this.name];
        }else{
            delete NetObj.rootObjs[this.name];
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

//TODO
//Attach, find children
//Override methods
//Delete
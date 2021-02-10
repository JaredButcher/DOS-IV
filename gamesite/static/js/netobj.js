let NetObj = /** @class */ (() => {
    class NetObj {
        constructor(kwargs) {
            this.id = -1;
            this.authority = 0;
            this.name = "";
            this.parent = null;
            this.children = {};
            this.rpcHandlers = {};
            for (let prop of Object.getOwnPropertyNames(Object.getPrototypeOf(this))) {
                if (this[prop] instanceof Function && prop.substr(0, 3) == 'rpc') {
                    this.rpcHandlers[prop] = this[prop];
                }
            }
            Object.assign(this, kwargs);
            NetObj.netObjs[this.id] = this;
            if (!this.parent) {
                NetObj.attachRootObj(this);
            }
        }
        static find(name) {
            let path = name.split('/');
            let obj = NetObj.rootObjs[path[0]];
            if (obj == undefined)
                return null;
            path.shift();
            for (let entry of path) {
                obj = obj.children[entry];
                if (obj == undefined)
                    return null;
            }
            return obj;
        }
        static attachRootObj(obj) {
            if (obj.parent) {
                delete obj.parent.children[obj.name];
            }
            obj.parent = null;
            NetObj.rootObjs[obj.name] = obj;
        }
        onLoad() {
            //On load, override
            if (this.parent) {
                this.parent = NetObj.netObjs[this.parent];
            }
            let children = {};
            Object.values(this.children).forEach((child) => {
                child = NetObj.netObjs[child];
                children[child.name] = child;
            });
        }
        onStart() {
            //Ran on game start, override
        }
        onUpdate(deltetime) {
            //Ran on each clock cycle, override
        }
        findChild(name) {
            let path = name.split('/');
            let obj = this;
            for (let entry of path) {
                obj = obj.children[entry];
                if (obj == undefined)
                    return null;
            }
            return obj;
        }
        attachChild(obj) {
            if (obj.parent) {
                delete obj.parent.children[obj.name];
            }
            obj.parent = this;
            this.children[obj.name] = obj;
        }
        command(procedure, args) {
            NetObj.send({ 'D': this.id, 'P': procedure, 'A': args });
        }
        handleServerRpc(message) {
            let rpc = this.rpcHandlers[message.P];
            if (message.P == "__del__") {
                this.destory();
            }
            else if (!rpc) {
                console.log("Failed to find rpc: " + message.P);
                console.log(this.rpcHandlers);
                console.log(this);
            }
            else {
                rpc.bind(this)(...message.A);
            }
        }
        destory() {
            if (this.parent) {
                delete this.parent.children[this.name];
            }
            else {
                delete NetObj.rootObjs[this.name];
            }
            this._destory();
        }
        _destory() {
            delete NetObj.netObjs[this.id];
            Object.values(this.children).forEach((obj) => {
                obj._destory();
            });
            this.children = {};
        }
    }
    NetObj.netObjs = {};
    NetObj.rootObjs = {};
    NetObj.localClientId = 0;
    return NetObj;
})();
export { NetObj };
//TODO
//Attach, find children
//Override methods
//Delete

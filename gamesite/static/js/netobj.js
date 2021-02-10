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
            if (this.parent == null) {
                if (NetObj.rootObj)
                    NetObj.rootObj.destory();
                NetObj.rootObj = this;
            }
        }
        static find(name) {
            return (NetObj.rootObj ? NetObj.rootObj.findChild(name) : null);
        }
        static clear() {
        }
        onLoad() {
            //On load, override and call super
            if (this.parent) {
                this.parent = NetObj.netObjs[this.parent];
                if (this.name in this.parent.children)
                    this.parent.children[this.name].destory();
                this.parent.children[this.name] = this;
            }
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
                NetObj.rootObj = null;
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
    NetObj.rootObj = null;
    NetObj.localClientId = 0;
    return NetObj;
})();
export { NetObj };

let NetObj = /** @class */ (() => {
    class NetObj {
        constructor(kwargs) {
            this.id = 0;
            this.authority = 0;
            this.type = Object.getPrototypeOf(this).constructor.name;
            Object.assign(this, kwargs);
            NetObj.netObjs[this.id] = this;
        }
        destory() {
            delete NetObj.netObjs[this.id];
        }
        static serverRpc(cls, funct) {
            if (!NetObj.serverRpcs[cls]) {
                NetObj.serverRpcs[cls] = {};
            }
            NetObj.serverRpcs[cls][funct.name] = funct;
            return funct;
        }
        static clientRpc(funct) {
            return (...args) => {
                if (NetObj.wsClient) {
                    NetObj.wsClient.send({ D: this.id, P: funct.name, A: args });
                }
                funct.bind(this)(...args);
            };
        }
        static handleServerRpc(message) {
            let netobj = NetObj.netObjs[message.D];
            if (netobj) {
                let rpcs = NetObj.serverRpcs[netobj.type];
                if (rpcs && rpcs[message.P]) {
                    rpcs[message.P].bind(netobj)(...message.A);
                }
            }
        }
    }
    NetObj.netObjs = {};
    NetObj.serverRpcs = {};
    return NetObj;
})();
export { NetObj };

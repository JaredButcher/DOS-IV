let NetObj = /** @class */ (() => {
    class NetObj {
        constructor(id, authority) {
            this.id = id;
            this.authority = authority;
            this.type = Object.getPrototypeOf(this).constructor.name;
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

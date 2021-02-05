let NetObj = /** @class */ (() => {
    class NetObj {
        constructor(kwargs) {
            this.id = -1;
            this.authority = 0;
            this.type = Object.getPrototypeOf(this).constructor.name;
            console.log(this);
            Object.assign(this, kwargs);
            console.log(this);
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
                    console.log({ D: this.id, P: funct.name, A: args });
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
                    if (message.P == "__del__") {
                        rpcs.destory();
                    }
                    else {
                        rpcs[message.P].bind(netobj)(...message.A);
                    }
                }
            }
        }
        static getObject(id, callback, onfail = () => { }) {
            if (id in NetObj.netObjs) {
                callback(NetObj.netObjs[id]);
            }
            else {
                onfail();
            }
        }
    }
    NetObj.netObjs = {};
    NetObj.serverRpcs = {};
    NetObj.localPlayerId = -1;
    NetObj.gameId = -1;
    return NetObj;
})();
export { NetObj };

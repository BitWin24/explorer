var mongoose = require('mongoose')
  , Schema = mongoose.Schema;

var PeersSchema = new Schema({
  rank: { type: String, default: "" },
  network: { type: String, default: "" },
  txHash: { type: String, default: "" },
  outidx: { type: String, default: "" },
  status: { type: String, default: "" },
  addr: { type: String, default: "" },
  ip: { type: String, default: "" },
  version: { type: String, default: "" },
  lastSeen: { type: Date, expires: 86400, default: Date.now()},
  activeTime: { type: Date, expires: 86400, default: Date.now()},
  lastpaid:{ type: String, default: "" }
});

module.exports = mongoose.model('Mnpeers', PeersSchema);
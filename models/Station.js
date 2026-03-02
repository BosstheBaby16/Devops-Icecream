const mongoose = require('mongoose');

const StationSchema = mongoose.Schema({
    id: {
        type: Number,
        required: true
    },
    date: {
        type: Date,
        default: Date.now
    },
    actual: {
        type: Number,
        required: true
    },
    target: {
        type: Number,
        required: true
    }
});

module.exports = mongoose.model('Station', StationSchema);
const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/db');
const User = require('./User');

const WearableData = sequelize.define('WearableData', {
    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    heartRate: {
        type: DataTypes.INTEGER,
        allowNull: false
    },
    steps: {
        type: DataTypes.INTEGER,
        allowNull: false
    },
    sleep: {
        type: DataTypes.FLOAT,
        allowNull: false
    },
    calories: {
        type: DataTypes.INTEGER,
        allowNull: false
    },
    stressLevel: {
        type: DataTypes.INTEGER,
        allowNull: false
    },
    timestamp: {
        type: DataTypes.DATE,
        defaultValue: DataTypes.NOW
    }
});

WearableData.belongsTo(User, { foreignKey: 'userId' });
User.hasMany(WearableData, { foreignKey: 'userId' });

module.exports = WearableData;

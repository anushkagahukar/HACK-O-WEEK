const WearableData = require('../models/WearableData');

const syncWearableData = async (req, res) => {
    try {
        const { heartRate, steps, sleep, calories, stressLevel } = req.body;

        if (!heartRate || !steps || !sleep || !calories || !stressLevel) {
            return res.status(400).json({ message: 'Please provide all wearable data fields' });
        }

        const dataEntry = await WearableData.create({
            userId: req.user.id,
            heartRate,
            steps,
            sleep,
            calories,
            stressLevel
        });

        res.status(201).json(dataEntry);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server Error' });
    }
};

const getWearableHistory = async (req, res) => {
    try {
        const history = await WearableData.findAll({
            where: { userId: req.user.id },
            order: [['timestamp', 'DESC']]
        });
        res.json(history);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server Error' });
    }
};

module.exports = {
    syncWearableData,
    getWearableHistory
};

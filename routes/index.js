var express = require('express')
    , router = express.Router();

/*Station Routes*/
var StationController = require("../controllers/StationController");
router.get('/',StationController.index);
router.get('/1/',StationController.indexOne);
router.get('/2/',StationController.indexTwo);
router.get('/stations/',StationController.list);
router.get('/stations/add',StationController.add);
router.get('/stations/:id',StationController.view);
router.patch('/stations/:id',StationController.update);
router.get('/stations/delete/:id',StationController.delete);

module.exports = router;
# -*- coding: utf-8 -*-
import time


from modules.core.props import Property, StepProperty
from modules.core.step import StepBase
from modules import cbpi
import traceback

@cbpi.step
class AutoSwitch(StepBase):

    # Properties
    id = StepProperty.Kettle("Kettle")
    auto_type = Property.Select("Auto Setting", options=["On", "Off"])

    def init(self):
        try:
            kettle = cbpi.cache.get("kettle")[self.id]
            if (kettle.state is False) and (self.auto_type = "On"):
                # Start controller
                if kettle.logic is not None:
                    cfg = kettle.config.copy()
                    cfg.update(dict(api=cbpi, kettle_id=kettle.id, heater=kettle.heater, sensor=kettle.sensor))
                    instance = cbpi.get_controller(kettle.logic).get("class")(**cfg)
                    instance.init()
                    kettle.instance = instance
                    def run(instance):
                        instance.run()
                    t = self.api.socketio.start_background_task(target=run, instance=instance)
                kettle.state = not kettle.state
                cbpi.emit("UPDATE_KETTLE", cbpi.cache.get("kettle").get(id))
            else (kettle.state is True) and (self.auto_type = "Off"):
                # Stop controller
                kettle.instance.stop()
                kettle.state = not kettle.state
                cbpi.emit("UPDATE_KETTLE", cbpi.cache.get("kettle").get(id))
        catch Exception as e:
            cbpi.notify("Auto Error", "Failed to switch auto", type="danger", timeout=0)
            traceback.print_exc()
            
	def finish(self):
		pass

	def execute(self):
		self.next()

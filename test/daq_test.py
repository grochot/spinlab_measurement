import nidaqmx
with nidaqmx.Task() as task:
	task.ai_channels.add_ai_voltage_chan("6124/ai1")
	print(task.read())
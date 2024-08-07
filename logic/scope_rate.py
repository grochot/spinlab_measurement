def scope_rate(rate :str):
	rates = ["60MHz", "30MHz", "15MHz", "7.5MHz", "3.75MHz", "1.88MHz", "938kHz", "469kHz", "234kHz", "117kHz", "58.6kHz", "29.3kHz", "14.6kHz", "7.32kHz", "3.66kHz", "1.83kHz", "916Hz"]
	index = rates.index(rate)
	return index

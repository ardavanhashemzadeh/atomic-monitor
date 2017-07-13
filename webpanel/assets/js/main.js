$('.gage').knob({
	width: '60',
	height: '50',
	fgColor: '#4CAF50',
	inputColor: 'white',
	bgColor: '#212121',
	angleOffset: '-125',
	angleArc: '250',
	readOnly: 'true',
	min: 0,
	max: 100,
	format: function(value) {
		return value + '%';
	},
	font: 'sans-serif'
});
$('.gage2').knob({
	width: '60',
	height: '50',
	fgColor: '#4CAF50',
	inputColor: 'white',
	bgColor: '#212121',
	angleOffset: '-125',
	angleArc: '250',
	readOnly: 'true',
	min: 0,
	max: 100,
	font: 'sans-serif'
});
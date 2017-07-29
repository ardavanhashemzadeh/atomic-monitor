Pace.start();
var cpuPie = new Chartist.Pie('#cpu-gage', {
  	series: [30, 70]
}, {
  	total: 100,
  	donut: true,
  	donutWidth: 6,
  	donutSolid: true,
  	startAngle: 0,
  	showLabel: false
});
var count = 0;
cpuPie.on('draw', function(context) {
	if(count < 1) {
		var value = context.value;
		if(value < 70) {
			context.element.attr({
				style: 'fill: #4CAF50;'
			});
		}
		else if(value >= 70 && value < 90) {
			context.element.attr({
				style: 'fill: #F57C00;'
			});
		}
		else {
			context.element.attr({
				style: 'fill: #E53935;'
			});
		}
		count++;
	}
});


var ramPie = new Chartist.Pie('#ram-gage', {
  	series: [90, 10]
}, {
  	total: 100,
  	donut: true,
  	donutWidth: 6,
  	donutSolid: true,
  	startAngle: 0,
  	showLabel: false
});
var count2 = 0;
ramPie.on('draw', function(context) {
	if(count2 < 1) {
		var value = context.value;
		if(value < 70) {
			context.element.attr({
				style: 'fill: #4CAF50;'
			});
		}
		else if(value >= 70 && value < 90) {
			context.element.attr({
				style: 'fill: #F57C00;'
			});
		}
		else {
			context.element.attr({
				style: 'fill: #E53935;'
			});
		}
		count2++;
	}
});

var swapPie = new Chartist.Pie('#swap-gage', {
  	series: [75, 25]
}, {
  	total: 100,
  	donut: true,
  	donutWidth: 6,
  	donutSolid: true,
  	startAngle: 0,
  	showLabel: false
});
var count3 = 0;
swapPie.on('draw', function(context) {
	if(count3 < 1) {
		var value = context.value;
		if(value < 70) {
			context.element.attr({
				style: 'fill: #4CAF50;'
			});
		}
		else if(value >= 70 && value < 90) {
			context.element.attr({
				style: 'fill: #F57C00;'
			});
		}
		else {
			context.element.attr({
				style: 'fill: #E53935;'
			});
		}
		count3++;
	}
});






new Chartist.Line('#cpu-chart', {
	labels: ['9:00', '9:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30'],
	series: [
		[10, 5, 30, 45, 25, 25, 80, 20]
	]
}, 
{
	high: 100,
	low: 0,
	fullWidth: true,
	showArea: true,
	showPoint: false,
	stretch: true,
	lineSmooth: Chartist.Interpolation.cardinal({
		tension: 0
	}),
	axisY: {
		showGrid: true,
		showLabel: true,
		offset: 25
	},
	axisX: {
		showGrid: false
	}
});

new Chartist.Line('#ram-chart', {
	labels: ['9:00', '9:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30'],
	series: [
		{
			name: 'used',
			data: [2, 3, 2, 2, 2, 4, 5, 5]
		}
	]
}, 
{
	high: 16,
	low: 0,
	fullWidth: true,
	showArea: true,
	showPoint: false,
	stretch: true,
	lineSmooth: Chartist.Interpolation.step(),
	axisY: {
		showGrid: true,
		showLabel: true,
		offset: 25
	},
	axisX: {
		showGrid: false
	}
});

new Chartist.Line('#swap-chart', {
	labels: ['9:00', '9:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30'],
	series: [
		{
			name: 'used',
			data: [5, 0, 0, 1, 3, 0, 0, 1]
		}
	]
}, 
{
	high: 100,
	low: 0,
	fullWidth: true,
	showArea: true,
	showPoint: false,
	stretch: true,
	lineSmooth: Chartist.Interpolation.step(),
	axisY: {
		showGrid: true,
		showLabel: true,
		offset: 25
	},
	axisX: {
		showGrid: false
	}
});

new Chartist.Line('#load-chart', {
	labels: ['9:00', '9:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30'],
	series: [
		{
			name: '1min',
			data: [0.4, 0.3, 0.1, 0.1, 0.4, 0.1, 0.1, 0.2]
		},
		{
			name: '5min',
			data: [0.1, 0.1, 0.0, 0.0, 0.2, 0.3, 0.3, 0.1]
		},
		{
			name: '15min',
			data: [0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.1, 0.0]
		}
	]
}, 
{
	high: 1,
	low: 0,
	fullWidth: true,
	showArea: true,
	showPoint: false,
	stretch: true,
	lineSmooth: Chartist.Interpolation.step(),
	axisY: {
		showGrid: true,
		showLabel: true,
		offset: 25
	},
	axisX: {
		showGrid: false
	}
});

new Chartist.Line('#ping-chart', {
	labels: ['9:00', '9:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30'],
	series: [
		[10, 5, 30, 45, 25, 22, 80, 24]
	]
}, 
{
	high: 300,
	low: 0,
	fullWidth: true,
	showArea: true,
	showPoint: false,
	stretch: true,
	lineSmooth: Chartist.Interpolation.cardinal({
		tension: 0
	}),
	axisY: {
		showGrid: true,
		showLabel: true,
		offset: 25
	},
	axisX: {
		showGrid: false
	}
});

new Chartist.Line('#netdown-chart', {
	labels: ['9:00', '9:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30'],
	series: [
		[10, 5, 30, 45, 25, 25, 80, 20]
	]
}, 
{
	high: 500,
	low: 0,
	fullWidth: true,
	showArea: true,
	showPoint: false,
	stretch: true,
	lineSmooth: Chartist.Interpolation.cardinal({
		tension: 0
	}),
	axisY: {
		showGrid: true,
		showLabel: true,
		offset: 25
	},
	axisX: {
		showGrid: false
	}
});

new Chartist.Line('#netup-chart', {
	labels: ['9:00', '9:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30'],
	series: [
		[10, 5, 30, 45, 25, 25, 80, 20]
	]
}, 
{
	high: 500,
	low: 0,
	fullWidth: true,
	showArea: true,
	showPoint: false,
	stretch: true,
	lineSmooth: Chartist.Interpolation.cardinal({
		tension: 0
	}),
	axisY: {
		showGrid: true,
		showLabel: true,
		offset: 25
	},
	axisX: {
		showGrid: false
	}
});
Pace.stop();
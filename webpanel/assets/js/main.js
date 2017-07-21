//var CONFIG = require('config.json'); <-- require doesn't exist

// convert boot timestamp to user friendly
function convert_uptime(boot_time) {
	var uptime = '';
	
	// TODO
	
	return uptime;
}

// get list of servers
/*$(document).ready(function() {
	$.ajax({
		url: 'http://' + CONFIG.cm_host + ':' + CONFIG.cm_port + '/servers',
		success: function(data) {
			for(var i = 0, len = data.length; i < len; i++) {
				// grab data
				var name = data[i].name;
				var type = '';
				switch(data[i].type) {
					case 'GN':
						type = 'server';
						break;
					case 'DB':
						type = 'database';
						break;
					case 'EM':
						type = 'envelope';
						break;
					case 'WB':
						type = 'internet-explorer';
						break;
					case 'FW':
						type = 'fire';
						break;
					case 'AD':
						type = 'users';
						break;
					case 'VM':
						type = 'desktop';
						break;
					case 'FS':
						type = 'folder';
						break;
					case 'SY':
						type = 'lock';
						break;
					default:
						type = 'question';
						break;
				}
				var type = data[i].type;
				var mode = data[i].mode;
				var host = data[i].host;
				var port = data[i].port;
				
				// gather now status
				var status = '';
				var ping = '';
				var ram = 0;
				var cpu = 0;
				var boot = '';
				var io = 0;
				$.ajax({
					url: 'http://' + CONFIG.cm_host + ':' + CONFIG.cm_port + '/now/' + host + '/' + port,
					success: function(data) {
						if(data.status == 'online') {
							status = 1;
							ping = data.ping;
							ram = data.ram_percent;
							cpu = data.cpu_percent;
							boot = data.boot_time;
							io = data.disk_io;
						}
						else {
							status = 0;
						}
					}
				});
				
				// get ping color
				var pingColor = '';
				if(ping <= 100) {
					pingColor = 'good';
				}
				else if(ping <= 200) {
					pingColor = 'warn';
				}
				else {
					pingColor = 'bad';
				}
				
				// determine server health
				var serverHealthColor = '';
				if(status == 0) {
					serverHealthColor = 'bad';
				}
				else {
					if(mode == 0) {
						if(pingColor == 'bad' || cpu >= 90 || ram >= 90) {
							serverHealthColor = 'warn';
						}
						else {
							serverHealthColor = 'good';
						}
					}
					else if(mode == 1) {
						serverHealthColor = 'disabled';
					}
					else {
						serverHealthColor = 'tofix';
					}
				}
				
				// add servers
				var html_data = "";
				html_data += "<a class='server-box' href='#'>";
				html_data += "<input type='hidden' id='server" + i + "-host' value='" + host + "' />";
				html_data += "<input type='hidden' id='server" + i + "-port' value='" + port + "' />";
				if(status == 0) {
					html_data += "<div class='bar " + serverHealthColor + "'></div>";
					html_data += "<h2><span><i class='fa fa-" + type + "' aria-hidden='true'></i></span>" + name + "</h2>";
					html_data += "<h3>" + uptime + "</h3>";
					html_data += "<div class='first-row'>";
					html_data += "<div class='gage-box'><input id='server" + i + "-cpu' type='text' value='0' class='gage'><span>CPU</span></div>";
					html_data += "<div class='gage-box'><input id='server" + i + "-ram' type='text' value='0' class='gage'><span>RAM</span></div>";
					html_data += "<div class='gage-box'><input id='server" + i + "-io' type='text' value='0' class='gage2'><span>I/O</span></div>";
					html_data += "</div>";
					html_data += "<div id='server" + i + "-ping' class='ping text-disabled'>0 ms</div>";
					html_data += "</div>";
				}
				else {
					html_data += "<div class='bar " + serverHealthColor + "'></div>";
					html_data += "<h2><span><i class='fa fa-" + type + "' aria-hidden='true'></i></span>" + name + "</h2>";
					html_data += "<h3>" + uptime + "</h3>";
					html_data += "<div class='first-row'>";
					html_data += "<div class='gage-box'><input id='server" + i + "-cpu' type='text' value='" + cpu + "' class='gage'><span>CPU</span></div>";
					html_data += "<div class='gage-box'><input id='server" + i + "-ram' type='text' value='" + ram + "' class='gage'><span>RAM</span></div>";
					html_data += "<div class='gage-box'><input id='server" + i + "-io' type='text' value='" + io + "' class='gage2'><span>I/O</span></div>";
					html_data += "</div>";
					html_data += "<div id='server" + i + "-ping' class='ping text-" + ? + "'>" + ping + "</div>";
					html_data += "</div>";
				}
				
				$('#servers').append(html_data);
			}
		}
	});
});*/

Pace.start();
$('.gage').knob({
	width: '60',
	height: '50',
	inputColor: 'white',
	bgColor: '#212121',
	angleOffset: '-125',
	angleArc: '250',
	readOnly: 'true',
	font: 'sans-serif',
	min: 0,
	max: 100,
	font: 'sans-serif'
});
$('.gage').each(function() {
	var value = $(this).val();
	if(value >= 70 && value < 90) {
		$(this).trigger('configure', { 'fgColor': '#F57C00' });
	}
	else if(value >= 90) {
		$(this).trigger('configure', { 'fgColor': '#E53935' });
	}
	else {
		$(this).trigger('configure', { 'fgColor': '#4CAF50' });
	}
});

$('.gage2').knob({
	width: '60',
	height: '50',
	inputColor: 'white',
	bgColor: '#212121',
	angleOffset: '-125',
	angleArc: '250',
	readOnly: 'true',
	font: 'sans-serif',
	min: 0,
	max: 1
});
$('.gage2').each(function() {
	var value = $(this).val();
	if(value >= 0.7 && value < 0.9) {
		$(this).trigger('configure', { 'fgColor': '#F57C00' });
	}
	else if(value >= 0.9) {
		$(this).trigger('configure', { 'fgColor': '#E53935' });
	}
	else {
		$(this).trigger('configure', { 'fgColor': '#4CAF50' });
	}
});
Pace.stop();


$('.gage3').knob({
	width: '110',
	height: '70',
	inputColor: 'white',
	bgColor: '#212121',
	angleOffset: '-125',
	angleArc: '250',
	readOnly: 'true',
	font: 'sans-serif',
	min: 0,
	max: 100
});
$('.gage3').each(function() {
	var value = $(this).val().slice(0, -1);
	if(value >= 70 && value < 90) {
		$(this).trigger('configure', { 'fgColor': '#F57C00' });
	}
	else if(value >= 90) {
		$(this).trigger('configure', { 'fgColor': '#E53935' });
	}
	else {
		$(this).trigger('configure', { 'fgColor': '#4CAF50' });
	}
});






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



$('.graph-section').each(function() {
	$(this).hide();
})
$('#general').show();

function changeSection(id, section) {
	var i, tabcontent, tablinks;
	$('.graph-section').each(function() {
		$(this).hide().fadeOut(50);
	})

	$('.tab').each(function() {
		$(this).removeClass('active');
	})

	$('#' + section).fadeIn(50);
	$('#' + id).addClass('active');
}
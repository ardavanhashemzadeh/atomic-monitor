// get graph data, usage data, & specs
$(document).ready(function() {
	// get params
    var params = {};
    window.location.search.substr(1).split("&").forEach(function(item) {
        params[item.split("=")[0]] = item.split("=")[1]
	});
	
	// load list of servers to option menu
	$.ajax({
		data: {
			path: 'http://cm.watson.io:5001/server_names',
			type: 'servers'
		},
		url: 'get_data.php',
		success: function(data) {
			for(var i = 0, len = data.data.length; i < len; i++) {
                var id = data.data[i][0];
                var name = data.data[i][1];
                
                $('#graph-server').append("<option value='" + id + "'>" + name + "</option>");
            }
		}
	});

	// get server ID if not set
	var server_id = 1;
	if(typeof params['id'] !== "undefined") {
		server_id = params['id'];
	}

	// graph data
	$.ajax({

	});

	// disks data
	$.ajax({
		data: {
			path: 'http://cm.watson.io:5001/disks/' + server_id + '/',
			type: 'disks'
		},
		url: 'get_data.php',
		success: function(data) {
			for(var i = 0, len = data.data.length; i < len; i++) {
				var name = data.data[i].name;
				var percent = data.data[i].percent;
				var used = data.data[i].used;
				var total = data.data[i].total; // for future release

				var html_data = "";
				html_data += "<tr>";
				html_data += "  <td class='device'>" + name + "</td>";
				html_data += "  <td class='size'>" + total + " GB</td>";
				if(percent >= 70) {
					html_data += "  <td><div class='progress-bar'><span class='warn' style='width: " + percent + "%'></span></div></td>";
				}
				else if(percent >= 90) {
					html_data += "  <td><div class='progress-bar'><span class='bad' style='width: " + percent + "%'></span></div></td>";
				}
				else {
					html_data += "  <td><div class='progress-bar'><span class='good' style='width: " + percent + "%'></span></div></td>";
				}
				html_data += "</tr>";

				$('#disks').append(html_data);
			}
		}
	});

	// specs
	$.ajax({
		data: {
			path: 'http://cm.watson.io:5001/specs/' + server_id + '/',
			type: 'specs'
		},
		url: 'get_data.php',
		success: function(data) {
			$('#specs-servertype').text(get_type_name(data.data.server_type));
			$('#specs-mode').text(data.data.mode);
			$('#specs-hostname').text(data.data.hostname);
			$('#specs-ip').text(data.data.ip);
			$('#specs-mac').text(data.data.mac);
			$('#specs-availability').text(data.data.availability + '%');
			if(data.data.availability > 80) {
				$('#specs-availability').addClass('text-good');
			}
			else if(data.data.availability > 60) {
				$('#specs-availability').addClass('text-warn');
			}
			else {
				$('#specs-availability').addClass('text-bad');
			}
			$('#specs-os').text(data.data.os);
			$('#specs-cpubrand').text(data.data.cpu_brand);
			$('#specs-cpuspeed').text(data.data.cpu_speed);
			$('#specs-ram').text(data.data.ram);
			$('#specs-uptime').text(convert_uptime(data.data.uptime) + " - (" + data.data.uptime + ")");
			$('#specs-load1m').text(data.data.load[0]);
			if(data.data.load[0] > 1.00) {
				$('#specs-load1m').addClass('text-bad');
			}
			else if(data.data.load[0] > .80) {
				$('#specs-load1m').addClass('text-warn');
			}
			else {
				$('#specs-load1m').addClass('text-good');
			}
			$('#specs-load5m').text(data.data.load[1]);
			if(data.data.load[1] > 1.00) {
				$('#specs-load5m').addClass('text-good');
			}
			else if(data.data.load[1] > .80) {
				$('#specs-load5m').addClass('text-bad');
			}
			else {
				$('#specs-load5m').addClass('text-good');
			}
			$('#specs-load15m').text(data.data.load[2]);
			if(data.data.load[2] > 1.00) {
				$('#specs-load15m').addClass('text-bad');
			}
			else if(data.data.load[2] > .80) {
				$('#specs-load15m').addClass('text-warn');
			}
			else {
				$('#specs-load15m').addClass('text-good');
			}
		}
	});
});













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
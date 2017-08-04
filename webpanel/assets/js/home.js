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
	max: 101,
	font: 'sans-serif',
    draw : function () { $(this.i).val(this.cv + '%'); }
});
$('.gage').each(function() {
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
Pace.stop();
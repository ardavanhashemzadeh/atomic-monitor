// get list of servers
$(document).ready(function() {
	Pace.start();
	//url: 'http://' + CONFIG.cm_host + ':' + CONFIG.cm_port + '/home',
	var url = 'http://cm.watson.io:5001/home';
	$.ajax({
		url: 'get_data.php?url=' + encodeURIComponent(url),
		success: function(data) {
			var down_count = 0;
			var down_servers = [];
			var warn_count = 0;
			var warn_servers = [];
			var good_count = 0;
			var good_total = 0;
			var disabled_count = 0;
			var disabled_servers = [];
			var maintenance_count = 0;
			var maintenance_servers = [];

			for(var i = 0, len = data.data.length; i < len; i++) {
				// grab data
				var online = data.data[i].online;
				var mode = data.data[i].mode;
				var name = data.data[i].name;
				var type = get_icon(data.data[i].typ);
				var ping = Math.ceil(data.data[i].ping);
				var os = data.data[i].os;
				var uptime = convert_uptime(data.data[i].boottime);
				var load_1m = data.data[i].load_onemin;
				var load_5m = data.data[i].load_fivemin;
				var load_15m = data.data[i].load_fifteenmin;
				var cpu = data.data[i].cpu;
				var ram = data.data[i].ram;
				var disk = '0'; // TODO add disk status to /home in cm
				var network = '0'; // TODO add network status to /home in cm
				var diskStatus = '';
				if(data.data[i].disk_percent == 0) {
					diskStatus = 'Good';
				}
				else {
					diskStatus = disk[i].disk_status;
				}
				
				// determine server health
				// 0 = good
				// 1 = warn
				// 2 = down
				// 3 = disabled
				// 4 = maintenance
				var serverHealth = 0;
				
				// bar color
				var barColor = 'good';
				if(online) {
					if(mode == 0) {
						if(ping > 100 && ping <= 200) {
							barColor = 'warn';
						}
						else if(load_1m >= 1.00) {
							barColor = 'warn';
						}
						else if(load_5m >= 1.00) {
							barColor = 'warn';
						}
						else if(load_15m >= 1.00) {
							barColor = 'warn';
						}
						else if(cpu >= 90) {
							barColor = 'warn';
						}
						else if(ram >= 90) {
							barColor = 'warn';
						}
						else if(diskStatus != 'Good') {
							barColor = 'warn';
						}
					}
					else if(mode == 1) {
						barColor = 'disabled';
					}
					else if(mode == 2) {
						barColor = 'tofix';
					}
				}
				else {
					barColor = 'bad';
				}
				
				// ping color
				var pingColor = 'good';
				if(ping >= 100 && ping < 200) {
					pingColor = 'warn';
				}
				else if(ping >= 200) {
					pingColor = 'bad';
				}

				// load color
				var load_1mColor = 'good';
				var load_5mColor = 'good';
				var load_15mColor = 'good';
				if(load_1m >= .80 && load_1m < 1.00) {
					load_1mColor = 'warn';
				}
				else if(load_1m >= 1.00) {
					load_1mColor = 'bad';
				}
				if(load_5m >= .80 && load_5m < 1.00) {
					load_5mColor = 'warn';
				}
				else if(load_5m >= 1.00) {
					load_5mColor = 'bad';
				}
				if(load_15m >= .80 && load_15m < 1.00) {
					load_15mColor = 'warn';
				}
				else if(load_15m >= 1.00) {
					load_15mColor = 'bad';
				}

				// disk color
				var diskColor = 'good';
				if(diskStatus != 'Good') {
					diskColor = 'warn';
				}

				// add servers
				var html_data = "";
				html_data += "<a class='server-box' href='#'>";
				html_data += "  <div class='bar " + barColor + "'></div>";
				html_data += "  <h2>" + name + "<span><i class='fa fa-" + type + "' aria-hidden='true'></i></span></h2>";
				html_data += "  <h3><span><i class='fa fa-" + os + "' aria-hidden='true'></i></span>" + uptime + "</h3>";
				html_data += "  <div class='ping text-" + pingColor + "'>" + ping + " ms</div>";
				html_data += "  <div class='gages'>";
				html_data += "    <div class='gage-box'><input type='text' value='" + cpu + "' class='gage'><span>CPU</span></div>";
				html_data += "    <div class='gage-box'><input type='text' value='" + ram + "' class='gage'><span>RAM</span></div>";
				html_data += "    <div class='load-box'>";
				html_data += "      <div class='load-status'>";
				html_data += "        <h6 class='title'>1m Load:</h6>";
				html_data += "		  <h6 class='value text-"+ load_1mColor + "'>" + load_1m + "</h6>";
				html_data += "		</div>";
				html_data += "		<div class='load-status'>";
				html_data += "		  <h6 class='title'>5m Load:</h6>";
				html_data += "		  <h6 class='value text-"+ load_5mColor + "'>" + load_5m + "</h6>";
				html_data += "		</div>";
				html_data += "		<div class='load-status'>";
				html_data += "		  <h6 class='title'>15m Load:</h6>";
				html_data += "		  <h6 class='value text-"+ load_15mColor + "'>" + load_15m + "</h6>";
				html_data += "		</div>";
				html_data += "	</div>";
				html_data += "	</div>";
				html_data += "  <div class='disks'>";
				html_data += "    <p>Disks: <span class='text-" + diskColor + "'>" + diskStatus + "</span></p>";
				html_data += "  </div>";
				html_data += "</a>";

				// update info for status boxes
				good_total++;
				if(barColor == 'bad') {
					down_count++;
					down_servers.push(name);
				}
				else if(barColor == 'warn') {
					warn_count++;
					warn_servers.push(name);
				}
				else if(barColor == 'good') {
					good_count++;
				}
				else if(barColor == 'disabled') {
					disabled_count++;
					disabled_servers.push(name);
				}
				else if(barColor == 'tofix') {
					maintenance_count++;
					maintenance_servers.push(name);
				}
				
				$('#servers').append(html_data);
			}

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

			// add info to status boxes
			$('#status-bad-count').text(down_count);
			$('#status-warn-count').text(warn_count);
			$('#status-good-count').text(good_count);
			$('#status-disabled-count').text(disabled_count);
			$('#status-tofix-count').text(maintenance_count);
			
			if(down_servers.length == 0) {
				$('#status-bad-servers').text('n/a');
			}
			else {
				$('#status-bad-servers').text(down_servers.join(', '));
			}
			if(warn_servers.length == 0) {
				$('#status-warn-servers').text('n/a');
			}
			else {
				$('#status-warn-servers').text(warn_servers.join(', '));
			}
			$('#status-good-total').text('Total Servers: ' + good_total);
			if(disabled_servers.length == 0) {
				$('#status-disabled-servers').text('n/a');
			}
			else {
				$('#status-disabled-servers').text(disabled_servers.join(', '));
			}
			if(maintenance_servers.length == 0) {
				$('#status-tofix-servers').text('n/a');
			}
			else {
				$('#status-tofix-servers').text(maintenance_servers.join(', '));
			}
		}
	});
	Pace.stop();
});

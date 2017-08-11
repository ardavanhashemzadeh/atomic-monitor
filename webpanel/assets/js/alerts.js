function levelToHTML(level) {
    switch(level) {
        case '0':
            return "<span class='warn'>Warning</span>";
        case '1':
            return "<span class='bad'>Error</span>";
        default:
            return "<span class='disabled'>???</span>";
    }
}

function strToDate(str_date) {
    var time = str_date.split(' ')[0].split('-');
    var fixedDate = new Date(time[0] + '-' + time[1] + '-' + time[2] + 'T' + str_date.split(' ')[1]);
    
    return (fixedDate.getMonth() + 1) + '/' + fixedDate.getDate() + '/' + fixedDate.getFullYear().toString().slice(-2) + ' ' + ('0' + fixedDate.getHours()).slice(-2) + ':' + ('0' + fixedDate.getMinutes()).slice(-2) + ':' + ('0' + fixedDate.getSeconds()).slice(-2);
}

// TODO: 
function strdateToAgo(str_date) {
    var time = str_date.split(' ')[0].split('-');
    var fixedDate = new Date(time[0] + '-' + time[1] + '-' + time[2] + 'T' + str_date.split(' ')[1]);
	var diffDate = new Date(new Date() - fixedDate);

	var delta = diffDate / 1000;
	var days = Math.floor(delta / 86400);
	delta -= days * 86400;
	var hours = Math.floor(delta / 3600) % 24;
	delta -= hours * 3600;
	var minutes = Math.floor(delta / 60) % 60;
	delta -= minutes * 60;
    var seconds = delta % 60;
    
    if(days > 0) {
        if(days == 1) {
            return days + ' day';
        }
        else {
            return days + ' days';
        }
    }
    else if(hours > 0) {
        if(hours == 1) {
            return hours + ' hour';
        }
        else {
            return hours + ' hours';
        }
    }
    else if(minutes > 0) {
        if(minutes == 1) {
            return minutes + ' minute';
        }
        else {
            return minutes + ' minutes';
        }
    }
    else {
        if(seconds == 1) {
            return seconds + ' second';
        }
        else {
            return seconds + ' seconds';
        }
    }
}

function retrieveErrorLogs() {
    // get form data
    var alertLevel = $('#alertFilterLevel').val();
    var server = $('#alertFilterServer').val();
    var count = $('#alertNumLogs').val();
    var keywordsSearchFor = $('#alertKeywordKeep').val();
    var keywordsFilterOut = $('#alertKeywordRemove').val();

    // redirect user to new URL with parameters to load error logs
    var parameters = [];
    parameters.push('pathset=true');
    if(alertLevel > -1 && alertLevel < 2) {
        parameters.push('level=' + alertLevel);
    }
    if(server > 0) {
        parameters.push('server=' + server);
    }
    parameters.push('count=' + count);
    if(keywordsSearchFor != '') {
        parameters.push('search_for=' + encodeURIComponent(keywordsSearchFor));
    }
    if(keywordsFilterOut != '') {
        parameters.push('filter_out=' + encodeURIComponent(keywordsFilterOut));
    }

    var url = window.location.protocol + '//' + window.location.host + window.location.pathname;
    var count = 0;
    parameters.forEach(function(item, index) {
        if(count == 0) {
            url += '?' + item;
        }
        else {
            url += '&' + item;
        }
        count++;
    });
    window.location.href = url;
}

// load error logs based on options given by user
$(document).ready(function() {
    // get params
    var params = {};
    window.location.search.substr(1).split("&").forEach(function(item) {
        params[item.split("=")[0]] = item.split("=")[1]
    });

    var pathSet = false;
    var alertLevel = -1;
    var server = -1;
    var count = 50;
    var keywordsSearchFor = '';
    var keywordsFilterOut = '';
    var urlParams = '?';
    if(typeof params['pathset'] !== "undefined") {
        pathSet = params['pathset'];
    }
    if(typeof params['level'] !== "undefined") {
        alertLevel = params['level'];
        $('#alertFilterLevel').val(alertLevel);
    }
    $.ajax({
        data: {
            path: 'http://cm.watson.io:5001/server_names',
            type: 'servers'
        },
        url: 'get_data.php',
        success: function(data) {
            $('#alertFilterServer').append("<option value='-1'>All</option>");
            for(var i = 0, len = data.data.length; i < len; i++) {
                var id = data.data[i][0];
                var name = data.data[i][1];
                
                $('#alertFilterServer').append("<option value='" + id + "'>" + name + "</option>");
            }
        }
    }).done(function() {
        if(typeof params['server'] !== "undefined") {
            server = params['server'];
            $('#alertFilterServer').val(server);
        }
    });
    if(typeof params['server'] !== "undefined") {
        server = params['server'];
    }
    if(typeof params['count'] !== "undefined") {
        count = params['count'];
        $('#alertNumLogs').val(count);
    }
    if(typeof params['search_for'] !== "undefined") {
        keywordsSearchFor = decodeURIComponent(params['search_for']);
        $('#alertKeywordKeep').val(keywordsSearchFor);
    }
    if(typeof params['filter_out'] !== "undefined") {
        keywordsFilterOut = decodeURIComponent(params['filter_out']);
        $('#alertKeywordRemove').val(keywordsFilterOut);
    }

    // retrieve error logs if inputs are filled out
    if(pathSet) {
        $.ajax({
            data: {
                path: 'http://cm.watson.io:5001/all_logs',
                type: 'logs',
                level: alertLevel,
                id: server,
                count: count,
                search_for: keywordsSearchFor,
                filter_out: keywordsFilterOut
            },
            url: 'get_data.php',
            success: function(data) {
                Pace.start();
                
                $('#alerts-log').html('');
                for(var i = 0, len = data.data.length; i < len; i++) {
                    var level = data.data[i].level;
                    var name = data.data[i].name;
                    var message = data.data[i].msg;
                    var timestamp = data.data[i].timestamp;
                    
                    var html_data = "";
                    html_data += "<div class='log'>";
                    html_data += "  <div class='log-level'>" + levelToHTML(level) + "</div>";
                    html_data += "  <div class='log-server'>" + name + "</div>";
                    html_data += "  <div class='log-reason'>" + message + "</div>";
                    html_data += "  <div class='log-timestamp'><span>" + strdateToAgo(timestamp) + " ago</span> (" + strToDate(timestamp) + ")</div>";
                    html_data += "</div>";

                    $('#alerts-log').append(html_data);
                }
                
                Pace.stop();
            }
        });
    }
});
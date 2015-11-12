var $ = require('jquery'),
    _ = require('lodash'),
    moment = require('moment');

Date.prototype.subtractDays = function(days) {
    var dat = new Date(this.valueOf());
    dat.setDate(dat.getDate() - days);
    return dat;
};

module.exports = function(url, days, container) {
    // Activity Graph
    $.getJSON(url, function(resp) {

        var results = resp.activity,
            date = new Date(),
            cats = [];

        if (!results.length) {
            $('.no-activity-message').removeClass('hide');
            return;
        }

        for (var i = days; i >= 0; i--) {
            var new_date = moment(date.subtractDays(i)).format('MMM D');
            cats.push(new_date);
        }

        var final_data = cats.map(function(date) {
            var value = _.find(results, function(result) {
                var momentdate = moment(result.date, 'YYYY-MM-DD').format('MMM D');
                console.log(date, momentdate);

                return date === moment(result.date, 'YYYY-MM-DD').format('MMM D');
            });
            console.log(value);
            return value ? value.num_submissions : 0;
        });

        console.log('final_data', final_data);

        $(container).highcharts({
            chart: {
                type: 'column'
            },
            title: {
                text: null
            },
            colors: [
                '#666'
            ],
            xAxis: {
                categories: cats
            },
            yAxis: {
                title: {
                    text: '# of submissions'
                },
                allowDecimals: false
            },
            series: [{
                name: 'Submissions',
                data: final_data
            }],
            legend: {
                enabled: false
            },
            credits: {
                enabled: false
            }
        });
    });
};

Highcharts.chart('light_overview', {
    chart: {
        type: 'line'
    },
    title: {
        text: 'Light-Sensor Last Week'
    },
    xAxis: {
        type: 'datetime',
        ordinal: true,
        title: {
            text: 'Date'
        },
        categories: light_dates,
        labels: {
            formatter: function() {
                  return Highcharts.dateFormat('%a %H:%M', this.value);
             }
        },
        tickInterval: 10

    },
    yAxis: {
        title: {
            text: 'Light'
        }
    },
    plotOptions: {
        line: {
            dataLabels: {
                enabled: false
            },
            enableMouseTracking: false
        }
    },
    series: light_values
});
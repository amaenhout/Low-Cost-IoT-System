Highcharts.chart('temperature_overview', {
    chart: {
        type: 'line'
    },
    title: {
        text: 'Temperature Last Week'
    },
    xAxis: {
        type: 'datetime',
        ordinal: true,
        title: {
            text: 'Date'
        },
        categories: temp_dates,
        labels: {
            formatter: function() {
                  return Highcharts.dateFormat('%a %H:%M', this.value);
             }
        },
        tickInterval: 10

    },
    yAxis: {
        title: {
            text: 'Temperature (°C)'
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
    series: temp_values
});
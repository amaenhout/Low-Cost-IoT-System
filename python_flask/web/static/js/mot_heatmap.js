
Highcharts.chart(key, {
	chart: {
		type: 'heatmap',
		marginTop: 40,
		marginBottom: 80,
		plotBorderWidth: 1
	},
  
	title: {
		text: 'Machine Usage This Week'
	},

	xAxis: {
		categories: ['9','10','11','12','13','14','15','16','17']
	},

	yAxis: {
		categories: ['Friday', 'Thursday', 'Wednesday', 'Tuesday', 'Monday'],
		title: null
	},

	colorAxis: {
		reversed: false,
		min: 0,
		minColor: '#FFFFFF',
		max: 60,
		maxColor: '#e81313'
		// stops: [
		// 	[0, '#FFFFFF'],
		// 	[10, '#53d01d'],
		// 	[15, '#96b200'],
		// 	[30, '#bf8d00'],
		// 	[45, '#db6000'],
		// 	[60, '#e81313']
		// ]
	},

	legend: {
		align: 'right',
		layout: 'vertical',
		margin: 0,
		verticalAlign: 'top',
		y: 25,
		symbolHeight: 200

	},
  
	tooltip: {
		formatter: function () {
		return '<b> on ' + this.series.xAxis.categories[this.point.x] + '</b> between  <br><b>' + 
			this.series.yAxis.categories[this.point.x] + ' and '+ (this.series.yAxis.categories[this.point.x] + 1)+
			'machines 003 runned for' + this.point.value + '</b> minutes <br><b>'
		}
	},
  
	series: [{
		name: 'Data',
		borderWidth: 1,
		data: heatmap_values[key],
		dataLabels: {
		enabled: true,
		color: '#000000'
		}
	}]

});

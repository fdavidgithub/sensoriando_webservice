window.onload = function() {

{% for sensor in context.sensors %}        
    var ctx{{ forloop.counter }} = document.getElementById("{{ context.canva }}{{ forloop.counter }}").getContext('2d');
	window.myLine = new Chart(ctx{{ forloop.counter }}, config{{ forloop.counter }});
{% endfor %}

//    setInterval(function(){
        //config.datasets.data[2] := randomScalingFactor();
//	    windows.myLine.update();
//    },1000);
};

{% for sensor in context.sensors %}
        var config{{ forloop.counter }} = {
            type: '{{ sensor.type }}',
			
            data: {
                labels: [

{% for datum in sensor.data %}                
                    '{{ datum.group_dt }}',
{% endfor %}

                ],
                datasets: [{
					backgroundColor: window.chartColors.red,
					borderColor: window.chartColors.red,
					data: [

{% for datum in sensor.data %}
                    parseFloat('{{ datum.group_value }}'.replace(",", ".")),
{% endfor %}

                    ],
					fill: false,
				}, ]
			},
			
            options: {
				responsive: true,
                title: {
					display: true,
					text: '{{ context.title }}'
				},
                legend: false,
			    tooltips: {
					mode: 'index',
					intersect: false,
				},
				hover: {
					mode: 'nearest',
					intersect: true
				},
				scales: {
					xAxes: [{
						display: true,
						scaleLabel: {
							display: true,
                            labelString: '{{ sensor.label }}'
						}
					}],
					yAxes: [{
						display: true,
						scaleLabel: {
							display: true,
							labelString: '{{ sensor.unit.name }}'
						}
					}]
				}
			}
		};
{% endfor %}


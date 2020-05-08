window.onload = function() {

{% for sensor in context.sensors %}        
    var ctx{{ forloop.counter }} = document.getElementById("{{ context.canva }}{{ forloop.counter }}").getContext('2d');
	window.myLine = new Chart(ctx{{ forloop.counter }}, config{{ forloop.counter }});
{% endfor %}

    setInterval(function(){
        //config.datasets.data[2] := randomScalingFactor();
	    windows.myLine.update();
    },1000);
};

{% for sensor in context.sensors %}
        var config{{ forloop.counter }} = {
			type: 'line',
			
            data: {
                labels: [

{% for datum in context.data %}                
    {% if datum.id_sensor == sensor.id %}
        '{{ datum.group_dt }}',
    {% endif %}
{% endfor %}
                ],
                datasets: [{
					backgroundColor: window.chartColors.red,
					borderColor: window.chartColors.red,
					data: [

{% for datum in context.data %}
    {% if datum.id_sensor == sensor.id %}
        {{ datum.group_value }},
    {% endif %}
{% endfor %}

                    ],
					fill: false,
				}, ]
			},
			
            options: {
				responsive: true,
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
                            labelString: '{{ context.interval }}'
						}
					}],
					yAxes: [{
						display: true,
						scaleLabel: {
							display: true,
							labelString: '**unidade**'
						}
					}]
				}
			}
		};
{% endfor %}


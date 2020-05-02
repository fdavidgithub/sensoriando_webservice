window.onload = function() {

{% for sensor in context.sensors %}        
    var ctx{{ forloop.counter }} = document.getElementById("{{ context.canva }}{{ forloop.counter }}").getContext('2d');
	window.myLine = new Chart(ctx{{ forloop.counter }}, config{{ forloop.counter }});
{% endfor %}

};

{% for sensor in context.sensors %}
        var config{{ forloop.counter }} = {
			type: 'line',
			
            data: {
                labels: [

{% for datum in context.data %}                
    {% if datum.id_sensor == sensor.id %}
        '{{ datum.dt }}',
    {% endif %}
{% endfor %}
                ],
                datasets: [{
					backgroundColor: window.chartColors.red,
					borderColor: window.chartColors.red,
					data: [

{% for datum in context.data %}
    {% if datum.id_sensor == sensor.id %}
        {{ datum.payload_value }},
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
							display: false,
						}
					}],
					yAxes: [{
						display: true,
						scaleLabel: {
							display: true,
							labelString: 'ºC'
						}
					}]
				}
			}
		};
{% endfor %}


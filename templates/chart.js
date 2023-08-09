window.onload = function() {

{% for sensor in context.sensors %}
    {% if sensor.type != 'table' and sensor.type != 'display' %}
        var ctx{{ forloop.counter }} = document.getElementById("ChartDetail{{ forloop.counter }}").getContext('2d');
	    window.myLine = new Chart(ctx{{ forloop.counter }}, config{{ forloop.counter }});
    {% endif %}
{% endfor %}

//    setInterval(function(){
        //config.datasets.data[2] := randomScalingFactor();
//	    windows.myLine.update();
//    },1000);
};

{% for sensor in context.sensors %}
    {% if sensor.type != 'table' and sensor.type != 'display' %}
 
        var config{{ forloop.counter }} = {
            type: '{{ sensor.type }}',
			
            data: {
                labels: [
                    {% for datum in sensor.data %}                
                        '{{ datum.dtread }}',
                    {% endfor %}
                ],
                datasets: [{
                    label: '{{ sensor.unit }}',
                    pointStyle: 'circle',
                    pointRadius: 5,
					backgroundColor: 'white',
					borderColor: 'red',
					data: [
                        {% for datum in sensor.data %}
                            parseFloat('{{ datum.value }}'.replace(",", ".")),
                        {% endfor %}
                    ],
					fill: false,
				}, ]
			},
			
            options: {
                responsive: true,

                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: '{{ sensor.label }}'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: false,
                            text: 'Value'
                        }
                    }
                },

            }
		};

    {% endif %}
{% endfor %}

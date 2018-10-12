{% for context in contexts %}
    var ctx = document.getElementById("myChart{{forloop.counter}}").getContext('2d');

    var myChart = new Chart(ctx, {
        type: 'line',

        data: {
            labels: {{ context.axis_x|safe }},
            datasets: [{
                label: "{{ context.sensor }}",
                data: {{ context.values }},
            }]
        },

        options: {
            title: {
                display: true,
                position: 'top',
                text: ["{{ context.categ }}"],
                fontSize: 14
            }
        },

    });
{% endfor %}

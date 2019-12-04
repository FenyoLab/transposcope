$(function() {
    $( "#slider-rangeRead1" ).slider({
        range: true,
        min: -200,
        max: 200,
        step:1,
        values: [-150, -50 ],
        slide: function( event, ui ) {
            redraw([ui.values[0],ui.values[1]], [$( "#slider-rangeRead2" ).slider( "values", 0 ),$( "#slider-rangeRead2" ).slider( "values", 1 )]);
        }
    });
    $( "#amount" ).val( "$" + $( "#slider-range" ).slider( "values", 0 ) +
                       " - $" + $( "#slider-range" ).slider( "values", 1 ) );
});
$(function() {
    $( "#slider-rangeRead2" ).slider({
        range: true,
        min: -200,
        max: 200,
        step:1,
        values: [ 50, 150 ],
        slide: function( event, ui ) {
            redraw([$( "#slider-rangeRead1" ).slider( "values", 0 ),$( "#slider-rangeRead1" ).slider( "values", 1 )], [ui.values[0],ui.values[1]]);
        }
    });
    $( "#amount" ).val( "$" + $( "#slider-range" ).slider( "values", 0 ) +
                       " - $" + $( "#slider-range" ).slider( "values", 1 ) );
});
$(function() {
    $('#radio_group input').on('change', function() {
           var orien = $('input[name=read_type]:checked', '#radio_group').val();
           var table = {
               '-/-': [[-50, -50], [50, 50]],
               'G/-': [[-50, -50], [50, 150]],
               'J/-': [[-50, 50], [50, 50]],
               'L/-': [[-150, -50], [50, 50]],
               'G/G': [[25, 125], [75, 175]],
               'L/L': [[-175, -75], [-125, -25]],
               'J/J': [[-25, 75], [-75, 25]],
               'G/L': [[-150, -50], [50 , 150]],
               'J/L': [[-50, 50], [-175, -75]],
               'J/G': [[-50, 50], [75, 175]],
           }
           var r1 = table[orien][0],
               r2 = table[orien][1];

           $("#slider-rangeRead1").slider("values", 0, r1[0]);
           $("#slider-rangeRead1").slider("values", 1, r1[1]);
           $("#slider-rangeRead2").slider("values", 0, r2[0]);
           $("#slider-rangeRead2").slider("values", 1, r2[1]);
           redraw(r1, r2);
    });
});

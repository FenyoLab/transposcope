$(document).ready(function () {
    $(function() {

        $( "#update" )
          .button()
          .click(function() {
            setParameters({"x": $( "#x-axis option:selected" ).text(),
                           "y": $( "#y-axis option:selected" ).text(),
                           "outline": $( "#outline option:selected" ).text(),
                           "size": $( "#size option:selected" ).text(),
                           "fill": $( "#fill option:selected" ).text()});
            $( "#slider-rangeD" ).slider( "values", 0, 0);
            $( "#slider-rangeD" ).slider( "values", 1, 16);

            $( "#slider-rangeW" ).slider( "values", 0, 4 );
            $( "#slider-rangeW" ).slider( "values", 1, 15 );

            $( "#slider-rangeP" ).slider( "values", 0, 0 );
            $( "#slider-rangeP" ).slider( "values", 1, 1 );

            $( "#slider-rangeV" ).slider( "values", 0, 0 );
            $( "#slider-rangeV" ).slider( "values", 1, 20 );

            $( "#slider-rangeJ" ).slider( "values", 0, 0 );
            $( "#slider-rangeJ" ).slider( "values", 1, 12 );

            $( "#slider-rangeProb" ).slider( "values", 0, 0 );
            $( "#slider-rangeProb" ).slider( "values", 1, 1 );
          })

        $( "#x-axis" ).selectmenu();
        $( "#y-axis" ).selectmenu();
        $( "#outline" ).selectmenu();
        $( "#size" ).selectmenu();
        $( "#fill" ).selectmenu();



        $( "#slider-rangeD" ).slider({
          range: true,
          min: 0,
          max: 16,
          step: 0.01,
          values: [ 0, 16 ],
          slide: function( event, ui ) {

            $( "#depth" ).val( ui.values[ 0 ] + " - " + ui.values[ 1 ] );
            draw(ui.values,
                 [+$( "#slider-rangeW" ).slider( "values", 0 ), +$( "#slider-rangeW" ).slider( "values", 1 )],
                 [+$( "#slider-rangeP" ).slider( "values", 0 ), +$( "#slider-rangeP" ).slider( "values", 1 )],
                 [+$( "#slider-rangeV" ).slider( "values", 0 ), +$( "#slider-rangeV" ).slider( "values", 1 )],
                 [+$( "#slider-rangeJ" ).slider( "values", 0 ), +$( "#slider-rangeJ" ).slider( "values", 1 )],
                 [+$( "#slider-rangeProb" ).slider( "values", 0 ), +$( "#slider-rangeProb" ).slider( "values", 1 )]);
          }
        });
        $( "#depth" ).val($( "#slider-rangeD" ).slider( "values", 0 ) +
          " - " + $( "#slider-rangeD" ).slider( "values", 1 ) );

        $( "#slider-rangeW" ).slider({
          range: true,
          min: 4,
          max: 15,
          step: 0.01,
          values: [ 4, 15 ],
          slide: function( event, ui ) {

            $( "#width" ).val( ui.values[ 0 ] + " - " + ui.values[ 1 ] );
            draw([+$( "#slider-rangeD" ).slider( "values", 0 ), +$( "#slider-rangeD" ).slider( "values", 1 )],
                 ui.values,
                [+$( "#slider-rangeP" ).slider( "values", 0 ), +$( "#slider-rangeP" ).slider( "values", 1 )],
                [+$( "#slider-rangeV" ).slider( "values", 0 ), +$( "#slider-rangeV" ).slider( "values", 1 )],
                [+$( "#slider-rangeJ" ).slider( "values", 0 ), +$( "#slider-rangeJ" ).slider( "values", 1 )],
                [+$( "#slider-rangeProb" ).slider( "values", 0 ), +$( "#slider-rangeProb" ).slider( "values", 1 )]);
          }
        });
        $( "#width" ).val($( "#slider-rangeW" ).slider( "values", 0 ) +
          " - " + $( "#slider-rangeW" ).slider( "values", 1 ) );


        $( "#slider-rangeP" ).slider({
          range: true,
          min: 0,
          max: 1,
          step: 0.001,
          values: [ 0, 1 ],
          slide: function( event, ui ) {

            $( "#polya" ).val( ui.values[ 0 ] + " - " + ui.values[ 1 ] );
            draw([+$( "#slider-rangeD" ).slider( "values", 0 ), +$( "#slider-rangeD" ).slider( "values", 1 )],
                 [+$( "#slider-rangeW" ).slider( "values", 0 ), +$( "#slider-rangeW" ).slider( "values", 1 )],
                 ui.values,
                 [+$( "#slider-rangeV" ).slider( "values", 0 ), +$( "#slider-rangeV" ).slider( "values", 1 )],
                 [+$( "#slider-rangeJ" ).slider( "values", 0 ), +$( "#slider-rangeJ" ).slider( "values", 1 )],
                 [+$( "#slider-rangeProb" ).slider( "values", 0 ), +$( "#slider-rangeProb" ).slider( "values", 1 )]);
          }
        });
        $( "#polya" ).val($( "#slider-rangeP" ).slider( "values", 0 ) +
          " - " + $( "#slider-rangeP" ).slider( "values", 1 ) );

        $( "#slider-rangeV" ).slider({
          range: true,
          min: 0,
          max: 20,
          step: 0.01,
          values: [ 0, 20 ],
          slide: function( event, ui ) {

            $( "#variant" ).val( ui.values[ 0 ] + " - " + ui.values[ 1 ] );
            draw([+$( "#slider-rangeD" ).slider( "values", 0 ), +$( "#slider-rangeD" ).slider( "values", 1 )],
                 [+$( "#slider-rangeW" ).slider( "values", 0 ), +$( "#slider-rangeW" ).slider( "values", 1 )],
                 [+$( "#slider-rangeP" ).slider( "values", 0 ), +$( "#slider-rangeP" ).slider( "values", 1 )],
                 ui.values,
                 [+$( "#slider-rangeJ" ).slider( "values", 0 ), +$( "#slider-rangeJ" ).slider( "values", 1 )],
                 [+$( "#slider-rangeProb" ).slider( "values", 0 ), +$( "#slider-rangeProb" ).slider( "values", 1 )]);
          }
        });
        $( "#variant" ).val($( "#slider-rangeV" ).slider( "values", 0 ) +
          " - " + $( "#slider-rangeV" ).slider( "values", 1 ) );

        $( "#slider-rangeJ" ).slider({
          range: true,
          min: 0,
          max: 12,
          step: 0.01,
          values: [ 0, 12 ],
          slide: function( event, ui ) {

            $( "#junc" ).val( ui.values[ 0 ] + " - " + ui.values[ 1 ] );
            draw([+$( "#slider-rangeD" ).slider( "values", 0 ), +$( "#slider-rangeD" ).slider( "values", 1 )],
                 [+$( "#slider-rangeW" ).slider( "values", 0 ), +$( "#slider-rangeW" ).slider( "values", 1 )],
                 [+$( "#slider-rangeP" ).slider( "values", 0 ), +$( "#slider-rangeP" ).slider( "values", 1 )],
                 [+$( "#slider-rangeV" ).slider( "values", 0 ), +$( "#slider-rangeV" ).slider( "values", 1 )],
                 ui.values,
                 [+$( "#slider-rangeProb" ).slider( "values", 0 ), +$( "#slider-rangeProb" ).slider( "values", 1 )]);
          }
        });
        $( "#junc" ).val($( "#slider-rangeJ" ).slider( "values", 0 ) +
          " - " + $( "#slider-rangeJ" ).slider( "values", 1 ) );

        $( "#slider-rangeProb" ).slider({
          range: true,
          min: 0,
          max: 1,
          step: 0.001,
          values: [ 0, 1 ],
          slide: function( event, ui ) {

            $( "#prob" ).val( ui.values[ 0 ] + " - " + ui.values[ 1 ] );
            draw([+$( "#slider-rangeD" ).slider( "values", 0 ), +$( "#slider-rangeD" ).slider( "values", 1 )],
                 [+$( "#slider-rangeW" ).slider( "values", 0 ), +$( "#slider-rangeW" ).slider( "values", 1 )],
                 [+$( "#slider-rangeP" ).slider( "values", 0 ), +$( "#slider-rangeP" ).slider( "values", 1 )],
                 [+$( "#slider-rangeV" ).slider( "values", 0 ), +$( "#slider-rangeV" ).slider( "values", 1 )],
                 [+$( "#slider-rangeJ" ).slider( "values", 0 ), +$( "#slider-rangeJ" ).slider( "values", 1 )],
                 ui.values );
          }
        });
        $( "#prob" ).val($( "#slider-rangeProb" ).slider( "values", 0 ) +
          " - " + $( "#slider-rangeProb" ).slider( "values", 1 ) );

    });


});

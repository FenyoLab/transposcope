/*jslint browser: true*/
/*global $, updateData*/
/*jQuery*/

//$(function(){
//    var ink, d, x, y;
//    $(".ripplelink").click(function(e){
//    if($(this).find(".ink").length === 0){
//        $(this).prepend("<span class='ink'></span>");
//    }
//
//    ink = $(this).find(".ink");
//    ink.removeClass("animate");
//
//    if(!ink.height() && !ink.width()){
//        d = Math.max($(this).outerWidth(), $(this).outerHeight());
//        ink.css({height: d, width: d});
//    }
//
//    x = e.pageX - $(this).offset().left - ink.width()/2;
//    y = e.pageY - $(this).offset().top - ink.height()/2;
//
//    ink.css({top: y+'px', left: x+'px'}).addClass("animate");
//});
//});

function buildTable(table) {
    "use strict";
    console.log('table', table);
    var i = "",
        j = "",
        oldTable = "",
        newTable = "",
        thead = "",
        tbody = "",
        tr = "",
        td = "";
    oldTable = document.getElementById('data_table');
    newTable = oldTable.cloneNode();
    thead = document.createElement('thead');
    tr = document.createElement('tr');
//    console.log(table.Heading);
    for (i = 0; i < table.Heading.length; i += 1) {
        td = document.createElement('th');
        td.id = "header" + i;
//        td.onclick = (function () {
//            window.alert("yo");
//        });
        td.appendChild(document.createTextNode(table.Heading[i]));
        tr.appendChild(td);
    }
    td = document.createElement('th');
    td.id = "header" + 2;
    td.appendChild(document.createTextNode('UCSC'));
    tr.appendChild(td);
    thead.appendChild(tr);
    newTable.appendChild(thead);
    tbody = document.createElement('tbody');
    tbody.id = "insertions";
    for (i = 0; i < table.data.length; i += 1) {
        tr = document.createElement('tr');
//        td = document.createElement('td');
        console.log(i, table.data[i]);
        for (j = 0; j < table.data[i].length; j += 1) {
            td = document.createElement('td');
            var item = "";
            if (j == 1) {
                item = table.data[i][j][0];
                td.style.color = table.data[i][j][1];
            } else {
                item = table.data[i][j];
            }
            td.appendChild(document.createTextNode(item));
            tr.appendChild(td);
        }
        td = document.createElement('td');
        var a = document.createElement('a');
        var icon = document.createElement("span");
        icon.className ="glyphicon glyphicon-link";
        a.appendChild(icon);
        var temp = table.data[i][0].split('-');
        var chr = temp[0];
        var pos = temp[1].split('(')[0];
        a.href = "http://genome.ucsc.edu/cgi-bin/hgTracks?db=hg19&hubUrl=http://openslice.fenyolab.org/tracks/tipseq/hub-ovarian.txt&position="+chr+":"+(parseInt(pos,10)-1000)+"-"+(parseInt(pos,10)+1000);
        a.target = "_blank";
        td.appendChild(a);
        tr.appendChild(td);
        tr.onclick = (function () {
            return function () {
                updateData(this.cells[0].innerHTML);
            };
        })();
        tbody.appendChild(tr);
    }
    newTable.appendChild(tbody);
    oldTable.parentNode.replaceChild(newTable, oldTable);
    $(function(){
        var table = $("#data_table");
        $("#header0").text("ID ◇");
        $("#header1").text("Gene ◇");
        $("#header2").text("P ◇");
        $("#header3").text("UCSC");
        $("#header2").text($("#header2").text().substr(0,$("#header2").text().length-1)+"▿");//▵
        var rows = table.find('tr:gt(0)').toArray().sort(comparer(2))
        if (!this.asc){rows = rows.reverse(); $("#header"+$(this).index()).text($("#header"+$(this).index()).text().substr(0,$("#header1").text().length-1)+"▿");}
        this.asc = !this.asc
        for (var i = 0; i < rows.length; i++){table.append(rows[i])}
    });

    $(function(){
    $('table').each(function() {
        if($(this).find('thead').length > 0 && $(this).find('th').length > 0) {
            // Clone <thead>
            var $w	   = $(window),
                $t	   = $(this),
                $thead = $t.find('thead').clone(),
                $col   = $t.find('thead, tbody').clone();
            // Add class, remove margins, reset width and wrap table
            $t
            .addClass('sticky-enabled')
            .css({
                margin: 0,
                width: '100%'
            }).wrap('<div class="sticky-wrap" />');

            if($t.hasClass('overflow-y')) $t.removeClass('overflow-y').parent().addClass('overflow-y');

            // Create new sticky table head (basic)
            $t.after('<table class="sticky-thead" />');

            // If <tbody> contains <th>, then we create sticky column and intersect (advanced)
            if($t.find('tbody th').length > 0) {
                $t.after('<table class="sticky-col" /><table class="sticky-intersect" />');
            }

            // Create shorthand for things
            var $stickyHead  = $(this).siblings('.sticky-thead'),
                $stickyCol   = $(this).siblings('.sticky-col'),
                $stickyInsct = $(this).siblings('.sticky-intersect'),
                $stickyWrap  = $(this).parent('.sticky-wrap');

            $stickyHead.append($thead);
            $stickyCol
            .append($col)
                .find('thead th:gt(0)').remove()
                .end()
                .find('tbody td').remove();

            $stickyInsct.html('<thead><tr><th>'+$t.find('thead th:first-child').html()+'</th></tr></thead>');
            // Set widths
            var setWidths = function () {
                    $t
                    .find('thead th').each(function (i) {
                        $stickyHead.find('th').eq(i).width($(this).width());
                    })
                    .end()
                    .find('tr').each(function (i) {
                        $stickyCol.find('tr').eq(i).height($(this).height());
                    });

                    // Set width of sticky table head
                    $stickyHead.width($t.width());

                    // Set width of sticky table col
                    $stickyCol.find('th').add($stickyInsct.find('th')).width($t.find('thead th').width())
                },
                repositionStickyHead = function () {
                    // Return value of calculated allowance
                    var allowance = calcAllowance();

                    // Check if wrapper parent is overflowing along the y-axis
                    if($t.height() > $stickyWrap.height()) {
                        // If it is overflowing (advanced layout)
                        // Position sticky header based on wrapper scrollTop()
                        if($stickyWrap.scrollTop() > 0) {
                            // When top of wrapping parent is out of view
                            $stickyHead.add($stickyInsct).css({
                                opacity: 1,
                                top: $stickyWrap.scrollTop()
                            });
                        } else {
                            // When top of wrapping parent is in view
                            $stickyHead.add($stickyInsct).css({
                                opacity: 0,
                                top: 0
                            });
                        }
                    } else {
                        // If it is not overflowing (basic layout)
                        // Position sticky header based on viewport scrollTop
                        if($w.scrollTop() > $t.offset().top && $w.scrollTop() < $t.offset().top + $t.outerHeight() - allowance) {
                            // When top of viewport is in the table itself
                            $stickyHead.add($stickyInsct).css({
                                opacity: 1,
                                top: $w.scrollTop() - $t.offset().top
                            });
                        } else {
                            // When top of viewport is above or below table
                            $stickyHead.add($stickyInsct).css({
                                opacity: 0,
                                top: 0
                            });
                        }
                    }
                },
                repositionStickyCol = function () {
                    if($stickyWrap.scrollLeft() > 0) {
                        // When left of wrapping parent is out of view
                        $stickyCol.add($stickyInsct).css({
                            opacity: 1,
                            left: $stickyWrap.scrollLeft()
                        });
                    } else {
                        // When left of wrapping parent is in view
                        $stickyCol
                        .css({ opacity: 0 })
                        .add($stickyInsct).css({ left: 0 });
                    }
                },
                calcAllowance = function () {
                    var a = 0;
                    // Calculate allowance
                    $t.find('tbody tr:lt(3)').each(function () {
                        a += $(this).height();
                    });

                    // Set fail safe limit (last three row might be too tall)
                    // Set arbitrary limit at 0.25 of viewport height, or you can use an arbitrary pixel value
                    if(a > $w.height()*0.25) {
                        a = $w.height()*0.25;
                    }

                    // Add the height of sticky header
                    a += $stickyHead.height();
                    return a;
                };

            setWidths();

            $t.parent('.sticky-wrap').scroll($.throttle(10, function() {
                repositionStickyHead();
                repositionStickyCol();
            }));

            $w
            .load(setWidths)
            .resize($.debounce(250, function () {
                setWidths();
                repositionStickyHead();
                repositionStickyCol();
            }))
            .scroll($.throttle(10, repositionStickyHead));
        }
    });
});
}
